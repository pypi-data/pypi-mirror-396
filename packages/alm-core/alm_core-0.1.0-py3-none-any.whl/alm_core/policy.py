"""
Constitutional Policy Engine
Enforces hard constraints on agent actions before execution.
"""

from typing import List, Dict, Any, Optional


class PolicyViolationError(Exception):
    """Raised when an action violates a hard constraint."""
    
    def __init__(self, message: str, action: str = None, params: Dict[str, Any] = None):
        super().__init__(message)
        self.action = action
        self.params = params


class Constitution:
    """
    The Constitutional Policy Engine enforces deterministic rules
    that cannot be overridden by the LLM.
    
    This is a core novelty of ALM: Hard constraints are programmatic,
    not prompt-based.
    """
    
    def __init__(self, rules: List[Dict[str, Any]]):
        """
        Initialize with a set of rules.
        
        Example rules:
        [
            {"action": "delete_db", "allow": False},
            {"action": "email_client", "forbidden_params": {"domain": "gmail.com"}},
            {"action": "file_access", "allowed_paths": ["/safe/dir"]},
            {"action": "web_request", "forbidden_domains": ["malicious.com"]}
        ]
        
        Args:
            rules: List of rule dictionaries defining constraints
        """
        self.rules = rules
        self._validate_rules()
    
    def _validate_rules(self):
        """Ensure rules are well-formed."""
        for rule in self.rules:
            if "action" not in rule:
                raise ValueError(f"Rule missing 'action' field: {rule}")
    
    def validate_action(self, action_name: str, parameters: Dict[str, Any] = None) -> bool:
        """
        Deterministic check against the constitution.
        
        Args:
            action_name: Name of the action to validate
            parameters: Parameters being passed to the action
            
        Returns:
            True if action is allowed
            
        Raises:
            PolicyViolationError: If action violates any rule
        """
        if parameters is None:
            parameters = {}
        
        for rule in self.rules:
            # Skip rules for other actions
            if rule.get("action") != action_name:
                continue
            
            # 1. Check explicit deny
            if "allow" in rule and not rule["allow"]:
                raise PolicyViolationError(
                    f"Action '{action_name}' is constitutionally prohibited.",
                    action=action_name,
                    params=parameters
                )
            
            # 2. Check forbidden parameters
            if "forbidden_params" in rule:
                for param, forbidden_val in rule["forbidden_params"].items():
                    if parameters.get(param) == forbidden_val:
                        raise PolicyViolationError(
                            f"Parameter '{param}={forbidden_val}' is prohibited for '{action_name}'.",
                            action=action_name,
                            params=parameters
                        )
            
            # 3. Check forbidden domains (for web/email actions)
            if "forbidden_domains" in rule:
                url_or_domain = parameters.get("url") or parameters.get("domain") or parameters.get("to")
                if url_or_domain:
                    for forbidden_domain in rule["forbidden_domains"]:
                        if forbidden_domain in url_or_domain:
                            raise PolicyViolationError(
                                f"Domain '{forbidden_domain}' is prohibited for '{action_name}'.",
                                action=action_name,
                                params=parameters
                            )
            
            # 4. Check allowed paths (for file operations)
            if "allowed_paths" in rule:
                file_path = parameters.get("path") or parameters.get("file")
                if file_path:
                    allowed = any(file_path.startswith(allowed_path) 
                                for allowed_path in rule["allowed_paths"])
                    if not allowed:
                        raise PolicyViolationError(
                            f"Path '{file_path}' is outside allowed directories for '{action_name}'.",
                            action=action_name,
                            params=parameters
                        )
            
            # 5. Check required parameters
            if "required_params" in rule:
                missing = [p for p in rule["required_params"] if p not in parameters]
                if missing:
                    raise PolicyViolationError(
                        f"Action '{action_name}' missing required parameters: {missing}",
                        action=action_name,
                        params=parameters
                    )
        
        return True
    
    def add_rule(self, rule: Dict[str, Any]):
        """Add a new rule at runtime."""
        if "action" not in rule:
            raise ValueError(f"Rule missing 'action' field: {rule}")
        self.rules.append(rule)
    
    def remove_rule(self, action_name: str):
        """Remove all rules for a specific action."""
        self.rules = [r for r in self.rules if r.get("action") != action_name]
    
    def get_rules_for_action(self, action_name: str) -> List[Dict[str, Any]]:
        """Get all rules that apply to a specific action."""
        return [r for r in self.rules if r.get("action") == action_name]
    
    def is_action_allowed(self, action_name: str, parameters: Dict[str, Any] = None) -> bool:
        """
        Check if an action is allowed without raising an exception.
        
        Returns:
            True if allowed, False if prohibited
        """
        try:
            self.validate_action(action_name, parameters)
            return True
        except PolicyViolationError:
            return False
