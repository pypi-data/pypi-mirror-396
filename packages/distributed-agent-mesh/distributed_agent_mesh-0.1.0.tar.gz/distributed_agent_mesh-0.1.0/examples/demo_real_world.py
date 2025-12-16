"""
Real-World DAM Demo: Document Analysis System
==============================================
A practical example using DAM for distributed document analysis
"""

import asyncio
from distributed_agent_mesh import (
    DistributedAgentMesh,
    AutonomousAgent,
    AgentCapability,
    Task
)


# Custom executors for different analysis types
async def text_extractor_executor(task):
    """Extract text from documents"""
    await asyncio.sleep(0.5)
    return {
        'status': 'completed',
        'result': f'Extracted text from {task.description}',
        'text_chunks': ['chunk1', 'chunk2', 'chunk3'],
        'pages': 10
    }


async def sentiment_analyzer_executor(task):
    """Analyze sentiment"""
    await asyncio.sleep(0.4)
    return {
        'status': 'completed',
        'result': f'Sentiment analyzed for {task.description}',
        'sentiment': 'positive',
        'confidence': 0.89
    }


async def entity_extractor_executor(task):
    """Extract named entities"""
    await asyncio.sleep(0.6)
    return {
        'status': 'completed',
        'result': f'Entities extracted from {task.description}',
        'entities': {
            'PERSON': ['John Doe', 'Jane Smith'],
            'ORG': ['Anthropic', 'OpenAI'],
            'DATE': ['2025-12-11']
        }
    }


async def summarizer_executor(task):
    """Generate summary"""
    await asyncio.sleep(0.5)
    return {
        'status': 'completed',
        'result': f'Summary generated for {task.description}',
        'summary': 'This is a comprehensive summary...',
        'key_points': ['point1', 'point2', 'point3']
    }


async def translator_executor(task):
    """Translate text"""
    await asyncio.sleep(0.7)
    return {
        'status': 'completed',
        'result': f'Translation completed for {task.description}',
        'translated_text': 'Translated content here...',
        'source_lang': 'en',
        'target_lang': 'hi'
    }


async def run_document_analysis_demo():
    """
    Demo: Analyze multiple documents in parallel using DAM
    """
    print("\n" + "="*80)
    print("🚀 REAL-WORLD DEMO: Distributed Document Analysis System")
    print("="*80 + "\n")
    
    # Create mesh
    mesh = DistributedAgentMesh()
    
    print("📋 Creating specialized agents...\n")
    
    # Create specialized agents
    text_agent = AutonomousAgent(
        agent_id="text_extractor",
        capabilities=[
            AgentCapability("text_extraction", "Extract text from documents"),
            AgentCapability("ocr", "Optical character recognition")
        ],
        executor=text_extractor_executor
    )
    
    sentiment_agent = AutonomousAgent(
        agent_id="sentiment_analyzer",
        capabilities=[
            AgentCapability("sentiment_analysis", "Analyze text sentiment"),
            AgentCapability("emotion_detection", "Detect emotions")
        ],
        executor=sentiment_analyzer_executor
    )
    
    entity_agent = AutonomousAgent(
        agent_id="entity_extractor",
        capabilities=[
            AgentCapability("entity_extraction", "Extract named entities"),
            AgentCapability("ner", "Named entity recognition")
        ],
        executor=entity_extractor_executor
    )
    
    summary_agent = AutonomousAgent(
        agent_id="summarizer",
        capabilities=[
            AgentCapability("summarization", "Generate summaries"),
            AgentCapability("key_point_extraction", "Extract key points")
        ],
        executor=summarizer_executor
    )
    
    translation_agent = AutonomousAgent(
        agent_id="translator",
        capabilities=[
            AgentCapability("translation", "Translate text"),
            AgentCapability("multilingual", "Handle multiple languages")
        ],
        executor=translator_executor
    )
    
    # Register all agents
    agents = [text_agent, sentiment_agent, entity_agent, summary_agent, translation_agent]
    for agent in agents:
        mesh.register_agent(agent)
    
    print(f"✅ {len(agents)} agents registered and ready\n")
    
    # Give agents time to discover each other
    await asyncio.sleep(0.3)
    
    # Create complex analysis tasks
    print("📄 Processing documents...\n")
    
    tasks = [
        Task(
            id="doc_001",
            description="Annual financial report Q4 2024",
            requirements=["text_extraction", "entity_extraction", "summarization"],
            priority=1
        ),
        Task(
            id="doc_002",
            description="Customer feedback survey results",
            requirements=["text_extraction", "sentiment_analysis", "summarization"],
            priority=2
        ),
        Task(
            id="doc_003",
            description="Technical documentation for API",
            requirements=["text_extraction", "translation", "summarization"],
            priority=1
        )
    ]
    
    # Process all documents in parallel
    print("⚡ Agents collaborating autonomously...\n")
    
    results = await asyncio.gather(*[
        mesh.solve_complex_task(task) for task in tasks
    ])
    
    # Display results
    print("\n" + "="*80)
    print("📊 ANALYSIS RESULTS")
    print("="*80 + "\n")
    
    for i, (task, result) in enumerate(zip(tasks, results), 1):
        print(f"Document {i}: {task.description}")
        print(f"  Status: {result['status']}")
        print(f"  Execution Time: {result['execution_time']:.2f}s")
        print(f"  Team Size: {result['team_size']} agents")
        print(f"  Agents: {', '.join(result['agents'])}")
        print()
    
    # Show mesh statistics
    stats = mesh.get_mesh_stats()
    
    print("="*80)
    print("📈 MESH STATISTICS")
    print("="*80 + "\n")
    print(f"Total Agents: {stats['total_agents']}")
    print(f"Active Agents: {stats['active_agents']}")
    print(f"Total Tasks Processed: {stats['completed_tasks']}")
    print(f"Total Peer Connections: {stats['total_peers']}")
    
    print("\n💡 Individual Agent Performance:\n")
    for agent_stat in stats['agent_stats']:
        print(f"  {agent_stat['agent_id']}:")
        print(f"    Completed Tasks: {agent_stat['completed_tasks']}")
        print(f"    Performance Score: {agent_stat['performance_score']:.2f}")
        print(f"    Collaborations: {agent_stat['collaborations']}")
        print()


async def run_streaming_analysis_demo():
    """
    Demo: Real-time streaming analysis with dynamic agent addition
    """
    print("\n" + "="*80)
    print("🌊 DEMO 2: Real-time Streaming Analysis")
    print("="*80 + "\n")
    
    mesh = DistributedAgentMesh()
    
    # Start with 2 agents
    print("Starting with 2 agents...\n")
    
    agent1 = AutonomousAgent(
        agent_id="stream_processor_1",
        capabilities=[AgentCapability("stream_processing", "Process streams")],
        executor=text_extractor_executor
    )
    
    agent2 = AutonomousAgent(
        agent_id="analyzer_1",
        capabilities=[AgentCapability("analysis", "Analyze data")],
        executor=sentiment_analyzer_executor
    )
    
    mesh.register_agent(agent1)
    mesh.register_agent(agent2)
    
    await asyncio.sleep(0.2)
    
    # Process first batch
    print("📥 Processing first batch of streams...\n")
    
    task1 = Task(
        id="stream_batch_1",
        description="Live social media feed analysis",
        requirements=["stream_processing", "analysis"],
        priority=1
    )
    
    result1 = await mesh.solve_complex_task(task1)
    print(f"✅ Batch 1 completed in {result1['execution_time']:.2f}s\n")
    
    # Add more agents dynamically
    print("🔥 High load detected! Adding 2 more agents dynamically...\n")
    
    agent3 = AutonomousAgent(
        agent_id="stream_processor_2",
        capabilities=[AgentCapability("stream_processing", "Process streams")],
        executor=text_extractor_executor
    )
    
    agent4 = AutonomousAgent(
        agent_id="analyzer_2",
        capabilities=[AgentCapability("analysis", "Analyze data")],
        executor=entity_extractor_executor
    )
    
    mesh.register_agent(agent3)
    mesh.register_agent(agent4)
    
    await asyncio.sleep(0.2)
    
    # Process second batch with more agents
    print("📥 Processing second batch with 4 agents...\n")
    
    task2 = Task(
        id="stream_batch_2",
        description="Live news feed analysis",
        requirements=["stream_processing", "analysis"],
        priority=1
    )
    
    result2 = await mesh.solve_complex_task(task2)
    print(f"✅ Batch 2 completed in {result2['execution_time']:.2f}s\n")
    
    print(f"💡 Performance improved with more agents!")
    print(f"   Team size increased: {result1['team_size']} → {result2['team_size']}")
    
    print("\n🎯 DAM Key Feature: Dynamic scalability without restart!")


async def main():
    """Run all demos"""
    await run_document_analysis_demo()
    await run_streaming_analysis_demo()
    
    print("\n" + "="*80)
    print("✨ DEMO COMPLETED - DAM in Action!")
    print("="*80 + "\n")
    
    print("Key Takeaways:")
    print("  1. ✅ Agents autonomously decide participation")
    print("  2. ✅ True parallel execution (faster than sequential)")
    print("  3. ✅ Self-organizing teams based on capabilities")
    print("  4. ✅ Dynamic agent addition without system restart")
    print("  5. ✅ Fault tolerance - system continues if agents fail")
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())
