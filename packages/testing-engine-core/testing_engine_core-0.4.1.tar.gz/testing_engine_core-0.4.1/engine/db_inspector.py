"""
Database Inspector - Query and validate database state during tests
"""

import logging
from typing import Any, Dict, List, Optional
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from .config import DatabaseConfig

logger = logging.getLogger(__name__)


class DatabaseInspector:
    """
    Inspect and validate database state during E2E tests.
    
    Features:
    - Execute raw SQL queries
    - Assert records exist with specific conditions
    - Count records matching criteria
    - Clean up test data
    - Transaction support
    """
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine: Optional[Engine] = None
        self.session_factory = None
        self._connect()
    
    def _connect(self):
        """Establish database connection"""
        try:
            self.engine = create_engine(
                self.config.connection_string,
                pool_pre_ping=True,
                echo=False
            )
            self.session_factory = sessionmaker(bind=self.engine)
            logger.info(f"✅ Connected to database: {self.config.database}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            raise
    
    @contextmanager
    def session(self):
        """Context manager for database sessions"""
        session: Session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results as dictionaries.
        
        Args:
            sql: SQL query string
            params: Query parameters
        
        Returns:
            List of row dictionaries
        """
        with self.session() as session:
            result = session.execute(text(sql), params or {})
            columns = result.keys()
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            logger.debug(f"📊 Query returned {len(rows)} rows")
            return rows
    
    def query_one(self, sql: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Execute a SQL query and return first result.
        
        Args:
            sql: SQL query string
            params: Query parameters
        
        Returns:
            First row as dictionary or None
        """
        results = self.query(sql, params)
        return results[0] if results else None
    
    def execute(self, sql: str, params: Optional[Dict[str, Any]] = None) -> int:
        """
        Execute a SQL statement (INSERT, UPDATE, DELETE).
        
        Args:
            sql: SQL statement
            params: Statement parameters
        
        Returns:
            Number of affected rows
        """
        with self.session() as session:
            result = session.execute(text(sql), params or {})
            affected = result.rowcount
            logger.debug(f"✏️ Statement affected {affected} rows")
            return affected
    
    def assert_record_exists(
        self,
        table: str,
        conditions: Dict[str, Any],
        timeout: int = 5
    ) -> Dict[str, Any]:
        """
        Assert that a record exists matching the given conditions.
        
        Args:
            table: Table name
            conditions: Dictionary of column=value conditions
            timeout: Timeout in seconds
        
        Returns:
            The matching record
        
        Raises:
            AssertionError: If no matching record found
        """
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            where_clause = " AND ".join([f"{key} = :{key}" for key in conditions.keys()])
            sql = f"SELECT * FROM {table} WHERE {where_clause}"
            
            result = self.query_one(sql, conditions)
            if result:
                logger.info(f"✅ Found record in {table}: {conditions}")
                return result
            
            time.sleep(0.5)
        
        raise AssertionError(f"❌ Record not found in {table} with conditions: {conditions}")
    
    def assert_record_count(
        self,
        table: str,
        expected_count: int,
        conditions: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Assert that the number of records matches expected count.
        
        Args:
            table: Table name
            expected_count: Expected number of records
            conditions: Optional filter conditions
        
        Returns:
            Actual count
        
        Raises:
            AssertionError: If count doesn't match
        """
        if conditions:
            where_clause = " AND ".join([f"{key} = :{key}" for key in conditions.keys()])
            sql = f"SELECT COUNT(*) as count FROM {table} WHERE {where_clause}"
            result = self.query_one(sql, conditions)
        else:
            sql = f"SELECT COUNT(*) as count FROM {table}"
            result = self.query_one(sql)
        
        actual_count = result["count"] if result else 0
        
        if actual_count != expected_count:
            raise AssertionError(
                f"❌ Record count mismatch in {table}: expected {expected_count}, got {actual_count}"
            )
        
        logger.info(f"✅ Record count matches: {actual_count} in {table}")
        return actual_count
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user record by email"""
        return self.query_one("SELECT * FROM users WHERE email = :email", {"email": email})
    
    def get_notifications_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all notifications for a user"""
        return self.query(
            "SELECT * FROM notifications WHERE user_id = :user_id ORDER BY created_at DESC",
            {"user_id": user_id}
        )
    
    def get_admin_logs_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all admin logs for a user"""
        return self.query(
            "SELECT * FROM admin_logs WHERE user_id = :user_id ORDER BY logged_at DESC",
            {"user_id": user_id}
        )
    
    def cleanup_test_data(self, pattern: str = "test_%"):
        """
        Clean up test data from all tables.
        
        Args:
            pattern: Email pattern for test users (default: test_%)
        """
        try:
            # Get test user IDs
            test_users = self.query(
                "SELECT id FROM users WHERE email LIKE :pattern",
                {"pattern": pattern}
            )
            user_ids = [user["id"] for user in test_users]
            
            if not user_ids:
                logger.info("🧹 No test data to clean up")
                return
            
            # Delete from dependent tables first
            with self.session() as session:
                # Delete notifications
                result = session.execute(
                    text("DELETE FROM notifications WHERE user_id = ANY(:user_ids)"),
                    {"user_ids": user_ids}
                )
                logger.info(f"🧹 Deleted {result.rowcount} test notifications")
                
                # Delete admin logs
                result = session.execute(
                    text("DELETE FROM admin_logs WHERE user_id = ANY(:user_ids)"),
                    {"user_ids": user_ids}
                )
                logger.info(f"🧹 Deleted {result.rowcount} test admin logs")
                
                # Delete users
                result = session.execute(
                    text("DELETE FROM users WHERE id = ANY(:user_ids)"),
                    {"user_ids": user_ids}
                )
                logger.info(f"🧹 Deleted {result.rowcount} test users")
            
            logger.info("✅ Test data cleanup complete")
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup test data: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("🔌 Database connection closed")
