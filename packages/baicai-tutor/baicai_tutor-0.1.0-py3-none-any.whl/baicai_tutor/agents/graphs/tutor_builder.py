from baicai_base.agents.graphs.base_graph import BaseGraph
from baicai_base.services import LLM
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.graph import END, START, StateGraph

from baicai_tutor.agents.graphs.nodes import (
    AnalystNode,
    QuestionerNode,
    StudentsNode,
    SurveyorNode,
    UserNode,
)
from baicai_tutor.agents.graphs.state import TutorState


class TutorBuilder(BaseGraph):
    """
    Graph for building and evaluating tutor.
    """

    def __init__(
        self,
        llm=None,
        config=None,
        memory=None,
        logger=None,
    ) -> None:
        """
        Initialize the TutorBuilder with configuration, memory, and other parameters.

        Args:
            llm: An instance of the LLM for code generation. Defaults to None.
            config: Custom configuration for the graph. Defaults to None.
            memory: Memory setup for the tutor builder. Defaults to None.
            logger: Logger for logging messages. Defaults to None.
        """
        super().__init__(llm=llm, config=config, memory=memory, logger=logger)
        self.llm = llm or LLM().llm
        self.graph_name = "Tutor"

        # nodes
        self.analyst_node = AnalystNode(llm=self.llm)
        self.questioner_node = QuestionerNode(llm=self.llm)
        self.students_node = StudentsNode(llm=self.llm)
        self.surveyor_node = SurveyorNode(llm=self.llm)
        self.user_node = UserNode(llm=self.llm)
        # Graph
        self.graph = StateGraph(TutorState)

    def build(self):
        """
        Build the graph by adding nodes and edges.

        Returns:
            StateGraph: The compiled state graph.
        """
        # Nodes
        self.graph.add_node("surveyor", self.surveyor_node)
        self.graph.add_node("analyst", self.analyst_node)
        self.graph.add_node("questioner", self.questioner_node)
        self.graph.add_node("students_answer", self.students_node)
        self.graph.add_node("user_answer", self.user_node)
        # Edges
        self.graph.add_edge(START, "surveyor")
        self.graph.add_edge("surveyor", "analyst")
        self.graph.add_edge("analyst", "questioner")
        self.graph.add_edge("questioner", "students_answer")
        self.graph.add_edge("students_answer", "user_answer")
        self.graph.add_edge("user_answer", END)

        return self.graph.compile(checkpointer=self.memory)
