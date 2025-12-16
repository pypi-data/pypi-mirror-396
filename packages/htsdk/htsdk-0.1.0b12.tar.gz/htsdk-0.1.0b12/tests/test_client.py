import unittest
from unittest.mock import Mock, patch
from heaptree.client import Heaptree
from heaptree.response_wrappers import (
    CreateNodeResponse,
    ExecutionResponseWrapper,
    NodesResponseWrapper,
    UsagesResponseWrapper,
)
from heaptree.exceptions import HeaptreeException

class TestCreateNodeResponse(unittest.TestCase):
    def test_single_node_access(self):
        """Test convenient access to single node ID"""
        raw_response = {
            "node_ids": ["node-123"],
            "status": "SUCCESS",
            "execution_time_seconds": 45.2
        }
        
        result = CreateNodeResponse(raw_response)
        
        # Test single node access
        self.assertEqual(result.node_id, "node-123")
        self.assertEqual(result.node_ids, ["node-123"])
        
        # Test properties
        self.assertEqual(result.status, "SUCCESS")
        self.assertEqual(result.execution_time_seconds, 45.2)
    
    def test_multiple_nodes_access(self):
        """Test access to multiple node IDs"""
        raw_response = {
            "node_ids": ["node-123", "node-456"],
            "status": "SUCCESS",
            "execution_time_seconds": 120.5
        }
        
        result = CreateNodeResponse(raw_response)
        
        # Test multiple node access
        self.assertEqual(result.node_ids, ["node-123", "node-456"])
    
    def test_single_node_access_error_on_multiple(self):
        """Test that accessing .node_id raises error when multiple nodes exist"""
        raw_response = {
            "node_ids": ["node-123", "node-456"],
            "status": "SUCCESS",
            "execution_time_seconds": 60.0
        }
        
        result = CreateNodeResponse(raw_response)
        
        # Should raise ValueError when trying to access single node ID
        with self.assertRaises(ValueError) as cm:
            _ = result.node_id
        
        self.assertIn("Multiple nodes created", str(cm.exception))
        self.assertIn("Use .node_ids", str(cm.exception))
    
    def test_empty_nodes_response(self):
        """Test handling of empty node_ids response"""
        raw_response = {
            "node_ids": [],
            "status": "failed",
            "execution_time_seconds": 1.0
        }
        
        result = CreateNodeResponse(raw_response)
        
        # Test empty lists are handled correctly
        self.assertEqual(result.node_ids, [])
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.execution_time_seconds, 1.0)
        
        # Should raise ValueError when trying to access single node properties
        with self.assertRaises(ValueError) as cm:
            _ = result.node_id
        self.assertIn("No nodes were created", str(cm.exception))
    
    def test_missing_optional_fields(self):
        """Test handling when optional fields are missing"""
        raw_response = {
            "node_ids": ["node-123"]
            # status and execution_time_seconds are missing
        }
        
        result = CreateNodeResponse(raw_response)
        
        # Should use defaults for missing fields
        self.assertEqual(result.status, "unknown")
        self.assertEqual(result.execution_time_seconds, 0.0)


class TestHeaptreeSDK(unittest.TestCase):
    def setUp(self):
        self.client = Heaptree(api_key="test")

    @patch('heaptree.client.requests.post')
    def test_create_node_returns_node_creation_result(self, mock_post):
        """Test that create_node returns CreateNodeResponse instance"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "node_ids": ["node-123"],
            "status": "SUCCESS",
            "execution_time_seconds": 45.2
        }
        mock_post.return_value = mock_response
        
        result = self.client.create_node(
            num_nodes=1,
        )
        
        # Check that result is CreateNodeResponse instance
        self.assertIsInstance(result, CreateNodeResponse)
        self.assertEqual(result.node_id, "node-123")

    @patch('heaptree.client.requests.post')
    def test_create_node_failure(self, mock_post):
        """Test create_node with invalid API key"""
        # Mock failed API response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.side_effect = ValueError("Invalid JSON")  # Simulates API error
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response
        
        client = Heaptree(api_key="invalid")
        with self.assertRaises(HeaptreeException):
            client.create_node(num_nodes=1)


class TestExecutionResponseWrapper(unittest.TestCase):
    def test_successful_execution(self):
        """Test successful command/code execution response"""
        raw_response = {
            "output": "Hello World!",
            "error": "",
            "exit_code": 0,
            "execution_time_seconds": 2.5
        }
        
        result = ExecutionResponseWrapper(raw_response)
        
        self.assertEqual(result.output, "Hello World!")
        self.assertEqual(result.error, "")
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(result.success)
        self.assertEqual(result.execution_time_seconds, 2.5)
    
    def test_failed_execution(self):
        """Test failed command/code execution response"""
        raw_response = {
            "output": "",
            "error": "Command not found",
            "exit_code": 127,
            "execution_time_seconds": 0.1
        }
        
        result = ExecutionResponseWrapper(raw_response)
        
        self.assertEqual(result.output, "")
        self.assertEqual(result.error, "Command not found")
        self.assertEqual(result.exit_code, 127)
        self.assertFalse(result.success)
        self.assertEqual(result.execution_time_seconds, 0.1)
    
    def test_missing_optional_fields(self):
        """Test handling when optional fields are missing"""
        raw_response = {}
        
        result = ExecutionResponseWrapper(raw_response)
        
        # Should use defaults for missing fields
        self.assertEqual(result.output, "")
        self.assertEqual(result.error, "")
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(result.success)  # success is True when exit_code=0 and error=""
        self.assertEqual(result.execution_time_seconds, 0.0)

    def test_logs_property(self):
        """Test the logs property combines output and error"""
        # Test with output only
        raw_response = {
            "output": "Hello World!",
            "error": "",
            "exit_code": 0
        }
        result = ExecutionResponseWrapper(raw_response)
        self.assertEqual(result.logs, "Hello World!")
        
        # Test with error only
        raw_response = {
            "output": "",
            "error": "Error occurred",
            "exit_code": 1
        }
        result = ExecutionResponseWrapper(raw_response)
        self.assertEqual(result.logs, "Error occurred")
        
        # Test with both output and error
        raw_response = {
            "output": "Some output",
            "error": "Some error",
            "exit_code": 1
        }
        result = ExecutionResponseWrapper(raw_response)
        self.assertEqual(result.logs, "Some output\nSome error")


class TestNodesResponseWrapper(unittest.TestCase):
    def test_multiple_nodes(self):
        """Test response with multiple nodes"""
        raw_response = {
            "nodes": [
                {"node_id": "node-123", "status": "running", "type": "ubuntu"},
                {"node_id": "node-456", "status": "stopped", "type": "windows"}
            ]
        }
        
        result = NodesResponseWrapper(raw_response)
        
        self.assertEqual(result.count, 2)
        self.assertEqual(len(result.nodes), 2)
        self.assertEqual(result.node_ids, ["node-123", "node-456"])
        self.assertEqual(result.nodes[0]["status"], "running")
    
    def test_empty_nodes(self):
        """Test response with no nodes"""
        raw_response = {"nodes": []}
        
        result = NodesResponseWrapper(raw_response)
        
        self.assertEqual(result.count, 0)
        self.assertEqual(result.nodes, [])
        self.assertEqual(result.node_ids, [])
    
    def test_missing_nodes_field(self):
        """Test response when nodes field is missing"""
        raw_response = {}
        
        result = NodesResponseWrapper(raw_response)
        
        self.assertEqual(result.count, 0)
        self.assertEqual(result.nodes, [])
        self.assertEqual(result.node_ids, [])
    
    def test_nodes_without_node_id(self):
        """Test nodes that are missing node_id field"""
        raw_response = {
            "nodes": [
                {"node_id": "node-123", "status": "running"},
                {"status": "stopped"}  # Missing node_id
            ]
        }
        
        result = NodesResponseWrapper(raw_response)
        
        self.assertEqual(result.count, 2)
        self.assertEqual(result.node_ids, ["node-123"])  # Only nodes with node_id are included


class TestUsagesResponseWrapper(unittest.TestCase):
    def test_multiple_usages(self):
        """Test response with multiple usage records"""
        raw_response = {
            "usages": [
                {"cost": 1.50, "duration_seconds": 300.0, "node_type": "small"},
                {"cost": 3.20, "duration_seconds": 600.0, "node_type": "medium"}
            ]
        }
        
        result = UsagesResponseWrapper(raw_response)
        
        self.assertEqual(result.count, 2)
        self.assertEqual(result.total_cost, 4.70)
        self.assertEqual(result.total_duration_seconds, 900.0)
        self.assertEqual(len(result.usages), 2)
    
    def test_empty_usages(self):
        """Test response with no usage records"""
        raw_response = {"usages": []}
        
        result = UsagesResponseWrapper(raw_response)
        
        self.assertEqual(result.count, 0)
        self.assertEqual(result.total_cost, 0.0)
        self.assertEqual(result.total_duration_seconds, 0.0)
        self.assertEqual(result.usages, [])
    
    def test_missing_usages_field(self):
        """Test response when usages field is missing"""
        raw_response = {}
        
        result = UsagesResponseWrapper(raw_response)
        
        self.assertEqual(result.count, 0)
        self.assertEqual(result.total_cost, 0.0)
        self.assertEqual(result.total_duration_seconds, 0.0)
        self.assertEqual(result.usages, [])
    
    def test_usages_with_missing_cost_duration(self):
        """Test usage records missing cost or duration fields"""
        raw_response = {
            "usages": [
                {"cost": 1.50, "duration_seconds": 300.0},
                {"cost": 2.00},  # Missing duration
                {"duration_seconds": 400.0},  # Missing cost
                {}  # Missing both
            ]
        }
        
        result = UsagesResponseWrapper(raw_response)
        
        self.assertEqual(result.count, 4)
        self.assertEqual(result.total_cost, 3.50)  # 1.50 + 2.00 + 0.0 + 0.0
        self.assertEqual(result.total_duration_seconds, 700.0)  # 300.0 + 0.0 + 400.0 + 0.0


if __name__ == "__main__":
    unittest.main()
