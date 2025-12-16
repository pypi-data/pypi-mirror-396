"""
Test Scenario - DSL for defining E2E test scenarios
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from enum import Enum


class StepType(Enum):
    """Types of test steps"""
    HTTP_REQUEST = "http_request"
    WAIT_FOR_MESSAGE = "wait_for_message"
    ASSERT_DATABASE = "assert_database"
    ASSERT_MESSAGE = "assert_message"
    SLEEP = "sleep"
    CUSTOM = "custom"


@dataclass
class TestStep:
    """
    A single step in a test scenario.
    
    Attributes:
        type: Type of step to execute
        description: Human-readable description
        params: Step-specific parameters
        timeout: Optional timeout for this step
        skip_on_failure: Continue even if step fails
    """
    type: StepType
    description: str
    params: Dict[str, Any] = field(default_factory=dict)
    timeout: Optional[int] = None
    skip_on_failure: bool = False
    
    def __repr__(self):
        return f"TestStep({self.type.value}: {self.description})"


class TestScenario:
    """
    Declarative test scenario with multiple steps.
    
    Example:
        scenario = TestScenario("User Registration Flow")
        scenario.http_request(
            service="user",
            method="POST",
            endpoint="/api/users",
            data={"email": "test@example.com"}
        )
        scenario.wait_for_message(
            queue="user.created",
            contains={"email": "test@example.com"}
        )
        scenario.assert_database(
            table="users",
            conditions={"email": "test@example.com"}
        )
    """
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.steps: List[TestStep] = []
        self.setup_steps: List[TestStep] = []
        self.teardown_steps: List[TestStep] = []
        self.tags: List[str] = []
    
    def add_step(self, step: TestStep) -> "TestScenario":
        """Add a step to the scenario"""
        self.steps.append(step)
        return self
    
    def http_request(
        self,
        service: str,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        expected_status: int = 200,
        description: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> "TestScenario":
        """
        Add HTTP request step.
        
        Args:
            service: Service name (user, notification, admin)
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request body
            expected_status: Expected HTTP status code
            description: Step description
            timeout: Request timeout
        """
        step = TestStep(
            type=StepType.HTTP_REQUEST,
            description=description or f"{method} {endpoint}",
            params={
                "service": service,
                "method": method,
                "endpoint": endpoint,
                "data": data,
                "expected_status": expected_status
            },
            timeout=timeout
        )
        return self.add_step(step)
    
    def wait_for_message(
        self,
        queue: str,
        contains: Optional[Dict[str, Any]] = None,
        timeout: int = 10,
        description: Optional[str] = None
    ) -> "TestScenario":
        """
        Add wait for message step.
        
        Args:
            queue: Queue name to monitor
            contains: Expected message content (partial match)
            timeout: Wait timeout in seconds
            description: Step description
        """
        step = TestStep(
            type=StepType.WAIT_FOR_MESSAGE,
            description=description or f"Wait for message in {queue}",
            params={
                "queue": queue,
                "contains": contains or {}
            },
            timeout=timeout
        )
        return self.add_step(step)
    
    def assert_message(
        self,
        queue: str,
        expected_body: Dict[str, Any],
        timeout: int = 10,
        description: Optional[str] = None
    ) -> "TestScenario":
        """
        Add assert message step.
        
        Args:
            queue: Queue to check
            expected_body: Expected message body
            timeout: Timeout in seconds
            description: Step description
        """
        step = TestStep(
            type=StepType.ASSERT_MESSAGE,
            description=description or f"Assert message in {queue}",
            params={
                "queue": queue,
                "expected_body": expected_body
            },
            timeout=timeout
        )
        return self.add_step(step)
    
    def assert_database(
        self,
        table: str,
        conditions: Dict[str, Any],
        timeout: int = 5,
        description: Optional[str] = None
    ) -> "TestScenario":
        """
        Add database assertion step.
        
        Args:
            table: Table name
            conditions: Record conditions to match
            timeout: Timeout in seconds
            description: Step description
        """
        step = TestStep(
            type=StepType.ASSERT_DATABASE,
            description=description or f"Assert record in {table}",
            params={
                "table": table,
                "conditions": conditions
            },
            timeout=timeout
        )
        return self.add_step(step)
    
    def sleep(
        self,
        seconds: float,
        description: Optional[str] = None
    ) -> "TestScenario":
        """
        Add sleep step.
        
        Args:
            seconds: Sleep duration
            description: Step description
        """
        step = TestStep(
            type=StepType.SLEEP,
            description=description or f"Sleep for {seconds}s",
            params={"seconds": seconds}
        )
        return self.add_step(step)
    
    def custom_step(
        self,
        func: Callable,
        description: str,
        timeout: Optional[int] = None
    ) -> "TestScenario":
        """
        Add custom function step.
        
        Args:
            func: Function to execute
            description: Step description
            timeout: Timeout for function execution
        """
        step = TestStep(
            type=StepType.CUSTOM,
            description=description,
            params={"func": func},
            timeout=timeout
        )
        return self.add_step(step)
    
    def add_tag(self, tag: str) -> "TestScenario":
        """Add a tag to the scenario"""
        if tag not in self.tags:
            self.tags.append(tag)
        return self
    
    def setup(self, func: Callable) -> "TestScenario":
        """Add setup step"""
        step = TestStep(
            type=StepType.CUSTOM,
            description="Setup",
            params={"func": func}
        )
        self.setup_steps.append(step)
        return self
    
    def teardown(self, func: Callable) -> "TestScenario":
        """Add teardown step"""
        step = TestStep(
            type=StepType.CUSTOM,
            description="Teardown",
            params={"func": func}
        )
        self.teardown_steps.append(step)
        return self
    
    def __repr__(self):
        return f"TestScenario('{self.name}', {len(self.steps)} steps)"
