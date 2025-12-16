"""
Distributed Agent Mesh (DAM) - Production Implementation
A framework for autonomous agents that collaborate via P2P communication
"""

import asyncio
import json
import uuid
import time
from typing import Dict, List, Set, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Agent operational states"""
    IDLE = "idle"
    BUSY = "busy"
    COLLABORATING = "collaborating"
    OFFLINE = "offline"


@dataclass
class AgentCapability:
    """Represents an agent's capability"""
    name: str
    description: str
    relevance_threshold: float = 0.7
    max_parallel_tasks: int = 5


@dataclass
class Task:
    """Represents a task in the mesh"""
    id: str
    description: str
    requirements: List[str]
    priority: int = 1
    deadline: Optional[float] = None
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'description': self.description,
            'requirements': self.requirements,
            'priority': self.priority,
            'deadline': self.deadline,
            'context': self.context
        }


@dataclass
class Message:
    """P2P message structure"""
    type: str
    sender_id: str
    receiver_id: Optional[str]
    content: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def to_dict(self) -> Dict:
        return {
            'type': self.type,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'content': self.content,
            'timestamp': self.timestamp,
            'message_id': self.message_id
        }


class P2PNetwork:
    """Peer-to-Peer network infrastructure"""
    
    def __init__(self):
        self.nodes: Dict[str, 'AutonomousAgent'] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.routing_table: Dict[str, Set[str]] = defaultdict(set)
        self.broadcast_history: Set[str] = set()
        
    def register_node(self, agent_id: str, agent: 'AutonomousAgent'):
        """Register an agent as a network node"""
        self.nodes[agent_id] = agent
        logger.info(f"✅ Node registered: {agent_id}")
        
    def unregister_node(self, agent_id: str):
        """Remove an agent from the network"""
        if agent_id in self.nodes:
            del self.nodes[agent_id]
            # Clean routing table
            for routes in self.routing_table.values():
                routes.discard(agent_id)
            logger.info(f"❌ Node unregistered: {agent_id}")
    
    async def broadcast(self, message: Message, exclude: Optional[Set[str]] = None):
        """Broadcast message to all nodes"""
        exclude = exclude or set()
        message_hash = hashlib.md5(
            f"{message.sender_id}{message.timestamp}{message.type}".encode()
        ).hexdigest()
        
        # Prevent duplicate broadcasts
        if message_hash in self.broadcast_history:
            return
        self.broadcast_history.add(message_hash)
        
        logger.info(f"📡 Broadcasting {message.type} from {message.sender_id}")
        
        for node_id, agent in self.nodes.items():
            if node_id not in exclude and node_id != message.sender_id:
                await agent.receive_message(message)
    
    async def send_direct(self, message: Message):
        """Send direct message to specific agent"""
        if message.receiver_id and message.receiver_id in self.nodes:
            agent = self.nodes[message.receiver_id]
            await agent.receive_message(message)
            logger.debug(f"📨 Direct message: {message.sender_id} → {message.receiver_id}")
        else:
            logger.warning(f"⚠️ Receiver {message.receiver_id} not found")
    
    def discover_agents(self, capability: Optional[str] = None) -> List[str]:
        """Discover agents in the network"""
        if capability:
            return [
                agent_id for agent_id, agent in self.nodes.items()
                if any(cap.name == capability for cap in agent.capabilities)
            ]
        return list(self.nodes.keys())


class AutonomousAgent:
    """
    Autonomous agent with P2P collaboration capabilities
    """
    
    def __init__(
        self,
        agent_id: str,
        capabilities: List[AgentCapability],
        executor: Optional[Callable] = None
    ):
        self.id = agent_id
        self.capabilities = capabilities
        self.state = AgentState.IDLE
        self.peers: Set[str] = set()
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: List[str] = []
        self.executor = executor or self.default_executor
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.performance_score = 1.0
        self.collaboration_history: List[Dict] = []
        
    async def default_executor(self, task: Task) -> Dict[str, Any]:
        """Default task executor - override for custom logic"""
        await asyncio.sleep(0.5)  # Simulate work
        return {
            'status': 'completed',
            'result': f"Task {task.id} completed by {self.id}",
            'agent_id': self.id
        }
    
    async def receive_message(self, message: Message):
        """Receive and queue message"""
        await self.message_queue.put(message)
    
    async def process_messages(self):
        """Process incoming messages continuously"""
        while True:
            try:
                message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=0.1
                )
                await self.handle_message(message)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"❌ Error processing message: {e}")
    
    async def handle_message(self, message: Message):
        """Handle different message types"""
        handlers = {
            'task_broadcast': self.handle_task_broadcast,
            'collaboration_request': self.handle_collaboration_request,
            'collaboration_response': self.handle_collaboration_response,
            'capability_query': self.handle_capability_query,
            'task_result': self.handle_task_result,
            'peer_discovery': self.handle_peer_discovery
        }
        
        handler = handlers.get(message.type)
        if handler:
            await handler(message)
        else:
            logger.warning(f"⚠️ Unknown message type: {message.type}")
    
    async def handle_task_broadcast(self, message: Message):
        """Handle broadcasted task"""
        task_data = message.content.get('task')
        if not task_data:
            return
            
        # Reconstruct task from dict
        task = Task(
            id=task_data['id'],
            description=task_data['description'],
            requirements=task_data['requirements'],
            priority=task_data.get('priority', 1),
            deadline=task_data.get('deadline'),
            context=task_data.get('context', {})
        )
        
        # Decide if can contribute
        can_contribute = await self.can_contribute(task)
        
        if can_contribute:
            logger.info(f"✋ {self.id} interested in task {task.id}")
            # Note: In full P2P, this would send interest back to coordinator
            # For simplicity, coordinator will check can_contribute directly
    
    async def handle_collaboration_request(self, message: Message):
        """Handle collaboration request from another agent"""
        task_id = message.content.get('task_id')
        subtask = message.content.get('subtask')
        
        if self.state == AgentState.IDLE or len(self.active_tasks) < 3:
            logger.info(f"🤝 {self.id} accepting collaboration for {task_id}")
            
            # Accept collaboration
            response = Message(
                type='collaboration_response',
                sender_id=self.id,
                receiver_id=message.sender_id,
                content={
                    'task_id': task_id,
                    'accepted': True,
                    'estimated_time': 2.0
                }
            )
            # Add peer
            self.peers.add(message.sender_id)
    
    async def handle_collaboration_response(self, message: Message):
        """Handle collaboration response"""
        if message.content.get('accepted'):
            logger.info(f"✅ Collaboration accepted by {message.sender_id}")
            self.peers.add(message.sender_id)
    
    async def handle_capability_query(self, message: Message):
        """Respond to capability query"""
        response = Message(
            type='capability_response',
            sender_id=self.id,
            receiver_id=message.sender_id,
            content={
                'capabilities': [
                    {'name': cap.name, 'description': cap.description}
                    for cap in self.capabilities
                ],
                'state': self.state.value,
                'performance_score': self.performance_score
            }
        )
    
    async def handle_task_result(self, message: Message):
        """Handle task result from peer"""
        task_id = message.content.get('task_id')
        result = message.content.get('result')
        logger.info(f"📥 Received result for {task_id} from {message.sender_id}")
    
    async def handle_peer_discovery(self, message: Message):
        """Handle peer discovery"""
        peer_id = message.sender_id
        if peer_id != self.id:
            self.peers.add(peer_id)
            logger.info(f"🔍 Discovered peer: {peer_id}")
    
    async def can_contribute(self, task: Task) -> bool:
        """
        Autonomous decision: Can this agent contribute to the task?
        """
        # Check state
        if self.state == AgentState.OFFLINE:
            return False
        
        # Check availability
        if len(self.active_tasks) >= 5:
            return False
        
        # Check capability match
        relevance_score = await self.analyze_relevance(task)
        if relevance_score < 0.7:
            return False
        
        # Check deadline feasibility
        if task.deadline:
            estimated_time = await self.estimate_completion_time(task)
            if time.time() + estimated_time > task.deadline:
                return False
        
        return True
    
    async def analyze_relevance(self, task: Task) -> float:
        """Calculate how relevant this task is to agent's capabilities"""
        # First check for exact capability name matches in requirements
        my_capability_names = {cap.name.lower() for cap in self.capabilities}
        task_requirements = {req.lower() for req in task.requirements}
        
        # Exact matches
        exact_matches = my_capability_names & task_requirements
        if exact_matches:
            return 1.0  # Perfect match
        
        # Fuzzy keyword matching
        task_keywords = set(task.description.lower().split())
        task_keywords.update(req.lower() for req in task.requirements)
        
        max_score = 0.0
        for capability in self.capabilities:
            cap_keywords = set(capability.name.lower().split('_'))
            cap_keywords.update(capability.description.lower().split())
            
            overlap = len(task_keywords & cap_keywords)
            total = len(task_keywords | cap_keywords)
            
            if total > 0:
                score = overlap / total
                max_score = max(max_score, score)
        
        return max_score
    
    async def estimate_completion_time(self, task: Task) -> float:
        """Estimate time to complete task"""
        base_time = 2.0
        complexity_factor = len(task.requirements) * 0.5
        return base_time + complexity_factor
    
    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute a task"""
        self.state = AgentState.BUSY
        self.active_tasks[task.id] = task
        
        logger.info(f"⚙️ {self.id} executing task {task.id}")
        
        try:
            result = await self.executor(task)
            self.completed_tasks.append(task.id)
            del self.active_tasks[task.id]
            self.state = AgentState.IDLE
            
            # Update performance score
            self.performance_score = min(1.0, self.performance_score + 0.01)
            
            return result
        except Exception as e:
            logger.error(f"❌ Task execution failed: {e}")
            self.performance_score = max(0.5, self.performance_score - 0.05)
            del self.active_tasks[task.id]
            self.state = AgentState.IDLE
            raise
    
    async def collaborate_with(
        self,
        other_agent: 'AutonomousAgent',
        task: Task
    ) -> Dict[str, Any]:
        """
        P2P collaboration with another agent
        """
        logger.info(f"🤝 {self.id} collaborating with {other_agent.id}")
        
        self.state = AgentState.COLLABORATING
        other_agent.state = AgentState.COLLABORATING
        
        # Share context
        my_context = {
            'capabilities': [cap.name for cap in self.capabilities],
            'performance_score': self.performance_score,
            'completed_tasks': len(self.completed_tasks)
        }
        
        their_context = {
            'capabilities': [cap.name for cap in other_agent.capabilities],
            'performance_score': other_agent.performance_score,
            'completed_tasks': len(other_agent.completed_tasks)
        }
        
        # Divide work
        my_subtask, their_subtask = await self.negotiate_work_division(
            task, my_context, their_context
        )
        
        # Execute in parallel
        results = await asyncio.gather(
            self.execute_task(my_subtask),
            other_agent.execute_task(their_subtask)
        )
        
        # Merge results
        combined = await self.merge_results(results[0], results[1])
        
        self.state = AgentState.IDLE
        other_agent.state = AgentState.IDLE
        
        # Record collaboration
        self.collaboration_history.append({
            'partner': other_agent.id,
            'task_id': task.id,
            'timestamp': time.time()
        })
        
        return combined
    
    async def negotiate_work_division(
        self,
        task: Task,
        my_context: Dict,
        their_context: Dict
    ) -> tuple[Task, Task]:
        """Negotiate how to divide work between agents"""
        # Simple division: split requirements
        mid = len(task.requirements) // 2
        
        my_subtask = Task(
            id=f"{task.id}_subtask_1",
            description=f"Part 1: {task.description}",
            requirements=task.requirements[:mid] if mid > 0 else task.requirements,
            priority=task.priority,
            context=task.context
        )
        
        their_subtask = Task(
            id=f"{task.id}_subtask_2",
            description=f"Part 2: {task.description}",
            requirements=task.requirements[mid:] if mid > 0 else [],
            priority=task.priority,
            context=task.context
        )
        
        return my_subtask, their_subtask
    
    async def merge_results(
        self,
        my_result: Dict[str, Any],
        their_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge results from collaborative work"""
        return {
            'status': 'completed',
            'combined_result': {
                'part_1': my_result,
                'part_2': their_result
            },
            'collaborators': [self.id, their_result.get('agent_id')]
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            'agent_id': self.id,
            'state': self.state.value,
            'capabilities': [cap.name for cap in self.capabilities],
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.completed_tasks),
            'performance_score': self.performance_score,
            'peers': len(self.peers),
            'collaborations': len(self.collaboration_history)
        }


class DistributedAgentMesh:
    """
    Main DAM system - Network of autonomous agents that collaborate
    """
    
    def __init__(self):
        self.network = P2PNetwork()
        self.agents: Dict[str, AutonomousAgent] = {}
        self.tasks: Dict[str, Task] = {}
        self.task_results: Dict[str, Any] = {}
        self.teams: Dict[str, List[str]] = {}
        
    def register_agent(self, agent: AutonomousAgent):
        """Register agent to the mesh"""
        self.agents[agent.id] = agent
        self.network.register_node(agent.id, agent)
        
        logger.info(f"🌐 Agent {agent.id} joined mesh")
        logger.info(f"   Capabilities: {[cap.name for cap in agent.capabilities]}")
        
        # Start message processing
        asyncio.create_task(agent.process_messages())
        
        # Announce to network
        asyncio.create_task(self.announce_agent(agent))
    
    async def announce_agent(self, agent: AutonomousAgent):
        """Announce agent to the network"""
        message = Message(
            type='peer_discovery',
            sender_id=agent.id,
            receiver_id=None,
            content={
                'capabilities': [cap.name for cap in agent.capabilities]
            }
        )
        await self.network.broadcast(message)
    
    def unregister_agent(self, agent_id: str):
        """Remove agent from mesh"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            self.network.unregister_node(agent_id)
            logger.info(f"🌐 Agent {agent_id} left mesh")
    
    async def solve_complex_task(self, task: Task) -> Dict[str, Any]:
        """
        Agents collaborate autonomously to solve task
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"🎯 New Complex Task: {task.description}")
        logger.info(f"{'='*60}\n")
        
        self.tasks[task.id] = task
        start_time = time.time()
        
        # 1. Broadcast task to network
        await self.broadcast_task(task)
        
        # 2. Agents autonomously decide to participate
        interested_agents = await self.gather_interested_agents(task)
        
        if not interested_agents:
            logger.warning("⚠️ No agents interested in task")
            return {'status': 'failed', 'reason': 'no_agents'}
        
        logger.info(f"✅ {len(interested_agents)} agents interested")
        
        # 3. Self-organize into team
        team = await self.self_organize_team(interested_agents, task)
        
        logger.info(f"👥 Team formed: {[agent.id for agent in team]}")
        
        # 4. Agents collaborate peer-to-peer
        result = await self.coordinate_team_collaboration(team, task)
        
        execution_time = time.time() - start_time
        result['execution_time'] = execution_time
        
        self.task_results[task.id] = result
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✨ Task completed in {execution_time:.2f}s")
        logger.info(f"{'='*60}\n")
        
        return result
    
    async def broadcast_task(self, task: Task):
        """Broadcast task to all agents"""
        message = Message(
            type='task_broadcast',
            sender_id='mesh_coordinator',
            receiver_id=None,
            content={'task': task.to_dict()}
        )
        await self.network.broadcast(message)
    
    async def gather_interested_agents(self, task: Task) -> List[AutonomousAgent]:
        """Gather agents that can contribute"""
        interested = []
        
        # Check each agent directly (synchronous for simplicity)
        for agent_id, agent in self.agents.items():
            can_help = await agent.can_contribute(task)
            if can_help:
                interested.append(agent)
                logger.info(f"✋ {agent.id} interested in task")
        
        return interested
    
    async def self_organize_team(
        self,
        interested_agents: List[AutonomousAgent],
        task: Task
    ) -> List[AutonomousAgent]:
        """
        Agents self-organize into optimal team
        Uses performance scores and capability matching
        """
        # Score each agent
        agent_scores = []
        for agent in interested_agents:
            relevance = await agent.analyze_relevance(task)
            score = relevance * agent.performance_score
            agent_scores.append((agent, score))
        
        # Sort by score
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select top agents (max 4 for efficiency)
        team_size = min(4, len(agent_scores))
        team = [agent for agent, score in agent_scores[:team_size]]
        
        return team
    
    async def coordinate_team_collaboration(
        self,
        team: List[AutonomousAgent],
        task: Task
    ) -> Dict[str, Any]:
        """
        Coordinate P2P collaboration among team members
        """
        if len(team) == 1:
            # Single agent execution
            return await team[0].execute_task(task)
        
        # Multiple agents - parallel execution
        logger.info(f"⚡ Parallel execution with {len(team)} agents")
        
        # Divide task among team
        subtasks = self.divide_task(task, len(team))
        
        # Execute in parallel
        results = await asyncio.gather(*[
            agent.execute_task(subtask)
            for agent, subtask in zip(team, subtasks)
        ])
        
        # Merge all results
        merged = {
            'status': 'completed',
            'results': results,
            'team_size': len(team),
            'agents': [agent.id for agent in team]
        }
        
        return merged
    
    def divide_task(self, task: Task, num_parts: int) -> List[Task]:
        """Divide task into subtasks"""
        subtasks = []
        requirements_per_part = max(1, len(task.requirements) // num_parts)
        
        for i in range(num_parts):
            start_idx = i * requirements_per_part
            end_idx = start_idx + requirements_per_part if i < num_parts - 1 else len(task.requirements)
            
            subtask = Task(
                id=f"{task.id}_part_{i+1}",
                description=f"Part {i+1}: {task.description}",
                requirements=task.requirements[start_idx:end_idx],
                priority=task.priority,
                context=task.context
            )
            subtasks.append(subtask)
        
        return subtasks
    
    def get_mesh_stats(self) -> Dict[str, Any]:
        """Get comprehensive mesh statistics"""
        return {
            'total_agents': len(self.agents),
            'active_agents': sum(1 for a in self.agents.values() if a.state != AgentState.OFFLINE),
            'total_tasks': len(self.tasks),
            'completed_tasks': len(self.task_results),
            'total_peers': sum(len(a.peers) for a in self.agents.values()),
            'agent_stats': [agent.get_stats() for agent in self.agents.values()]
        }


# Example custom executors for different agent types
async def research_executor(task: Task) -> Dict[str, Any]:
    """Research agent executor"""
    await asyncio.sleep(1.0)  # Simulate research
    return {
        'status': 'completed',
        'result': f"Research completed: {task.description}",
        'findings': ['finding1', 'finding2', 'finding3']
    }


async def analysis_executor(task: Task) -> Dict[str, Any]:
    """Analysis agent executor"""
    await asyncio.sleep(0.8)  # Simulate analysis
    return {
        'status': 'completed',
        'result': f"Analysis completed: {task.description}",
        'metrics': {'accuracy': 0.95, 'confidence': 0.88}
    }


async def visualization_executor(task: Task) -> Dict[str, Any]:
    """Visualization agent executor"""
    await asyncio.sleep(0.6)  # Simulate visualization
    return {
        'status': 'completed',
        'result': f"Visualization created: {task.description}",
        'charts': ['chart1.png', 'chart2.png']
    }
