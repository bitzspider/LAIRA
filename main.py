#!/usr/bin/env python3
import os
import logging
from dotenv import load_dotenv
from langchain_community.llms import OpenAI
from langchain_community.llms import Ollama
import gradio as gr
from search_tool import WebSearchScraper

load_dotenv()

MAINQUERY_COUNT = int(os.getenv("MAINQUERY_COUNT", "4"))
SUBQUERY_COUNT = int(os.getenv("SUBQUERY_COUNT", "2"))
NOTEBOOK_LINE_THRESHOLD = int(os.getenv("NOTEBOOK_LINE_THRESHOLD", "25"))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_researcher_llm(researcher_id):
    llm_name = os.getenv(f"RESEARCHER_{researcher_id}_LLM")
    llm_type = os.getenv(f"RESEARCHER_{researcher_id}_LLM_TYPE", "openai").lower()
    temperature = float(os.getenv(f"RESEARCHER_{researcher_id}_LLM_TEMPERATURE", "0"))
    if llm_type == "ollama":
        logger.info(f"Initializing Researcher {researcher_id} LLM with Ollama model: {llm_name}")
        return Ollama(model=llm_name)
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing in .env file")
        logger.info(f"Initializing Researcher {researcher_id} LLM with OpenAI model: {llm_name}")
        return OpenAI(api_key=api_key, model_name=llm_name, temperature=temperature)

def get_researcher_instructions(researcher_id):
    return os.getenv(f"RESEARCHER_{researcher_id}_INSTRUCTIONS", "")

def get_researcher_use_tools(researcher_id):
    return os.getenv(f"RESEARCHER_{researcher_id}_USE_TOOLS", "false").lower() in ["true", "1", "yes"]

class SearchResearcher:
    """
    Researcher1 (Search):
    1) Maintains a conversation history with the LLM.
    2) Generates main subqueries as CSV.
    3) Refines them.
    4) Executes web searches.
    5) Passes snippets to ReportResearcher for relevance checks.
    """
    def __init__(self, researcher_id):
        self.id = researcher_id
        self.instructions = get_researcher_instructions(researcher_id)
        self.use_tools = get_researcher_use_tools(researcher_id)
        self.scraper = WebSearchScraper()
        self.llm = initialize_researcher_llm(researcher_id)
        self.conversation = []
    def generate_main_subqueries(self, original_query):
        logger.info(f"Researcher {self.id} (Search): Generating {MAINQUERY_COUNT} search terms for: {original_query}")
        system_prompt = (
            "System: You are the 'Search Researcher'. Your job is to produce short, direct subqueries "
            "to help find relevant info about the user's topic. Do not add extra commentary.\n"
            f"{self.instructions}\n"
        )
        user_prompt = (
            f"User Query: {original_query}\n"
            f"Generate exactly {MAINQUERY_COUNT} subqueries, comma-separated."
        )
        messages = [{"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}]
        messages += self.conversation
        max_attempts = 3
        response = ""
        for attempt in range(max_attempts):
            try:
                response = self.llm.invoke(messages) if hasattr(self.llm, "invoke") else self.llm(messages)
                subqueries = [s.strip() for s in response.split(",") if s.strip()]
                if len(subqueries) == MAINQUERY_COUNT:
                    self.conversation.append({"role": "assistant", "content": response})
                    logger.info(f"Researcher {self.id} (Search): Main subqueries generated successfully.")
                    return response.strip()
                else:
                    correction = f"Error correction: Provide exactly {MAINQUERY_COUNT} comma-separated subqueries with no extra text."
                    logger.info(f"Researcher {self.id} (Search): Incorrect subquery count, requesting correction.")
                    messages.append({"role": "user", "content": correction})
            except Exception as e:
                logger.error(f"Researcher {self.id} (Search): Error generating subqueries: {e}")
                return ""
        return response.strip()
    def refine_to_subqueries(self, raw_subqueries, original_query, subquery_count):
        logger.info(f"Researcher {self.id} (Search): Refining subqueries to the best {subquery_count}.")
        system_prompt = (
            "System: You are 'CSV Output Researcher'. Refine the subqueries to keep them relevant. "
            "Do not add commentary; output exactly the requested number of comma-separated subqueries.\n"
            f"{self.instructions}\n"
        )
        user_prompt = (
            f"Given these subqueries: {raw_subqueries}\n"
            f"Refine them to the MOST RELEVANT {subquery_count} subqueries for a search engine, in CSV format.\n"
            f"Original Query: {original_query}\n"
            "Output only the CSV."
        )
        messages = [{"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}]
        messages += self.conversation
        max_attempts = 3
        response = ""
        for attempt in range(max_attempts):
            try:
                response = self.llm.invoke(messages) if hasattr(self.llm, "invoke") else self.llm(messages)
                subqueries = [s.strip() for s in response.split(",") if s.strip()]
                if len(subqueries) == subquery_count:
                    self.conversation.append({"role": "assistant", "content": response})
                    logger.info(f"Researcher {self.id} (Search): Refined subqueries generated successfully.")
                    return response.strip()
                else:
                    correction = f"Error correction: Provide exactly {subquery_count} comma-separated subqueries with no extra text."
                    logger.info(f"Researcher {self.id} (Search): Incorrect refined subquery count, requesting correction.")
                    messages.append({"role": "user", "content": correction})
            except Exception as e:
                logger.error(f"Researcher {self.id} (Search): Error refining subqueries: {e}")
                return ""
        return response.strip()
    def perform_search(self, subquery):
        clean_subquery = subquery.strip().strip('\'"')
        logger.info(f"Researcher {self.id} (Search): Performing web search for subquery: {clean_subquery}")
        try:
            raw_text = self.scraper.webSearch_text(clean_subquery)
            logger.info(f"Researcher {self.id} (Search): Search completed for subquery: {clean_subquery}")
        except Exception as e:
            logger.error(f"Researcher {self.id} (Search): Error during web search: {e}")
            raw_text = f"[Search failed for {clean_subquery}: {e}]"
        return raw_text

class ReportResearcher:
    """
    Researcher2 (Report):
    1) Check snippet relevance. If relevant, return the exact text from the snippet that is useful for the query.
    2) Generate a final report from the collected relevant snippet texts.
    """
    def __init__(self, researcher_id):
        self.id = researcher_id
        self.instructions = get_researcher_instructions(researcher_id)
        self.use_tools = get_researcher_use_tools(researcher_id)
        self.llm = initialize_researcher_llm(researcher_id)
        self.conversation = []
    def assess_snippet_relevance_and_summarize(self, user_query, snippet):
        logger.info(f"Researcher {self.id} (Report): Assessing snippet relevance.")
        prompt = (
            f"{self.instructions}\n"
            "We are collecting web-search information to answer the User Query.\n"
            "Your job is to analyze the snippet provided and output exactly the text from the snippet that is directly relevant to the User Query. Do not modify or add any commentary.\n"
            "If the snippet does not contain any relevant information, otherwise respond 'no'.\n\n"
            f"User Query: {user_query}\n\n"
            "Snippet:\n"
            f"{snippet}\n\n"
            "If relevant, output only the portions of the snippet that are useful. If not relevant, output only 'no'.\n\n"
        )
        logger.info(f"Researcher {self.id} (Report): Relevance check prompt:\n{prompt}")
        try:
            response = self.llm.invoke(prompt) if hasattr(self.llm, "invoke") else self.llm(prompt)
            logger.info(f"Researcher {self.id} (Report): Response:\n{response}")
            return response.strip()
        except Exception as e:
            logger.error(f"Researcher {self.id} (Report): Error assessing snippet: {e}")
            return "NO"
    def generate_final_report(self, user_query, researcher_notebook):
        logger.info(f"Researcher {self.id} (Report): Generating final report.")
        joined_info = "\n".join(researcher_notebook)
        prompt = (
            f"{self.instructions}\n"
            "You are the Report Researcher. Use the following relevant snippet texts to produce a comprehensive final answer to the User Query.\n\n"
            f"User Query: {user_query}\n\n"
            f"Relevant Snippet Texts:\n{joined_info}\n\n"
            "Provide a well-structured final answer using only the provided texts."
        )
        messages = [{"role": "system", "content": "System: Provide a final comprehensive answer using the provided texts."},
                    {"role": "user", "content": prompt}]
        messages += self.conversation
        max_attempts = 3
        response = ""
        for attempt in range(max_attempts):
            try:
                response = self.llm.invoke(messages) if hasattr(self.llm, "invoke") else self.llm(messages)
                if response and len(response.strip()) > 0:
                    self.conversation.append({"role": "assistant", "content": response})
                    logger.info(f"Researcher {self.id} (Report): Final report generated successfully.")
                    return response.strip()
                else:
                    correction = "Error correction: Provide a comprehensive final answer using only the provided texts."
                    logger.info(f"Researcher {self.id} (Report): Inadequate final report, requesting correction.")
                    messages.append({"role": "user", "content": correction})
            except Exception as e:
                logger.error(f"Researcher {self.id} (Report): Error generating final report: {e}")
                return f"Error generating final report: {e}"
        return response.strip()

class LeadResearcher:
    """
    Researcher0 (Lead):
    1) Determine if research is needed.
    2) If not, directly respond.
    3) If needed, coordinate between SearchResearcher and ReportResearcher until the final report is produced.
    """
    def __init__(self, researcher_id, tools):
        self.id = researcher_id
        self.instructions = get_researcher_instructions(researcher_id)
        self.use_tools = get_researcher_use_tools(researcher_id)
        self.llm = initialize_researcher_llm(researcher_id)
        self.tools = tools
        self.search_researcher = None
        self.report_researcher = None
        for tool in tools:
            role = os.getenv(f"RESEARCHER_{tool.id}_ROLE", "").lower()
            if role == "search" and self.search_researcher is None:
                self.search_researcher = tool
            elif role == "report" and self.report_researcher is None:
                self.report_researcher = tool
        if self.search_researcher is None and tools:
            self.search_researcher = tools[0]
        if self.report_researcher is None and tools:
            self.report_researcher = tools[0]
        self.direct_answer = ""
    def should_research(self, query):
        prompt = (
            f"{self.instructions}\n"
            "Answer ONLY 'yes' if a web search is required to answer the query; otherwise, answer directly.\n"
            f"User Query: {query}"
        )
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                response = self.llm.invoke(prompt) if hasattr(self.llm, "invoke") else self.llm(prompt)
                if "yes" in response.lower():
                    logger.info(f"LeadResearcher {self.id}: Research required as per response.")
                    return True
                else:
                    prompt += "\nError correction: For this query, you must answer 'yes' to perform research."
                    logger.info(f"LeadResearcher {self.id}: Forcing research with error correction, attempt {attempt+1}.")
            except Exception as e:
                logger.error(f"LeadResearcher {self.id}: Error in should_research: {e}")
                break
        return True
    def process_query(self, user_query):
        logger.info(f"LeadResearcher {self.id}: process_query started with query: {user_query}")
        if not self.use_tools:
            logger.info(f"LeadResearcher {self.id}: Tools disabled. Returning direct answer.")
            return f"No research performed. Query was: {user_query}"
        if not self.should_research(user_query):
            logger.info(f"LeadResearcher {self.id}: No research needed. Returning direct answer.")
            return self.direct_answer
        notebook = []
        notebook_dir = "./notebook"
        os.makedirs(notebook_dir, exist_ok=True)
        notebook_file_path = os.path.join(notebook_dir, "notebook.txt")
        with open(notebook_file_path, "w", encoding="utf-8") as f:
            f.write("")
        round_num = 0
        max_rounds = 3
        while round_num < max_rounds:
            logger.info(f"LeadResearcher {self.id}: Starting research round {round_num+1}.")
            main_subqueries = self.search_researcher.generate_main_subqueries(user_query)
            refined_subqueries = self.search_researcher.refine_to_subqueries(main_subqueries, user_query, SUBQUERY_COUNT)
            best_subqueries = [s.strip() for s in refined_subqueries.split(",") if s.strip()]
            for subquery in best_subqueries:
                logger.info(f"LeadResearcher {self.id}: Searching with subquery: {subquery}")
                search_results_text = self.search_researcher.perform_search(subquery)
                lines = [line for line in search_results_text.split("\n") if line.strip()]
                logger.info(f"LeadResearcher {self.id}: Found {len(lines)} snippet lines for subquery: {subquery}")
                for idx, snippet in enumerate(lines):
                    logger.info(f"LeadResearcher {self.id}: Processing snippet {idx+1}/{len(lines)}.")
                    summary = self.report_researcher.assess_snippet_relevance_and_summarize(user_query, snippet)
                    if summary.upper().strip() != "NO":
                        if summary not in notebook:
                            notebook.append(summary)
                            logger.info(f"LeadResearcher {self.id}: New relevant snippet added to notebook.\nNote: {summary}")
                            with open(notebook_file_path, "a", encoding="utf-8") as f:
                                f.write(summary + "\n")
                        else:
                            logger.info(f"LeadResearcher {self.id}: Duplicate snippet detected; skipping addition.")
                        if len(notebook) >= NOTEBOOK_LINE_THRESHOLD:
                            logger.info(f"LeadResearcher {self.id}: Notebook threshold reached. Generating final report.")
                            final_report = self.report_researcher.generate_final_report(user_query, notebook)
                            return final_report
            round_num += 1
            if not notebook:
                logger.info(f"LeadResearcher {self.id}: No relevant info collected. Instructing agents to retry.")
                instruction = "Error correction: Previous searches did not yield relevant results. Please generate alternative subqueries and reattempt."
                self.search_researcher.conversation.append({"role": "user", "content": instruction})
                self.report_researcher.conversation.append({"role": "user", "content": instruction})
        final_report = self.report_researcher.generate_final_report(user_query, notebook)
        return final_report

def initialize_research_team():
    researcher_ids = set()
    for key in os.environ:
        if key.startswith("RESEARCHER_") and key.endswith("_LLM"):
            parts = key.split("_")
            if len(parts) >= 3:
                researcher_ids.add(parts[1])
    lead_id = None
    tools = []
    for rid in sorted(researcher_ids, key=int):
        role = os.getenv(f"RESEARCHER_{rid}_ROLE", "").lower()
        if role == "lead":
            lead_id = rid
        elif role == "search":
            tools.append(SearchResearcher(rid))
        elif role == "report":
            tools.append(ReportResearcher(rid))
        else:
            tools.append(ReportResearcher(rid))
    if lead_id is None:
        raise ValueError("No lead researcher (role=lead) found in .env configuration.")
    return LeadResearcher(lead_id, tools)

def laira_interface(query):
    logger.info(f"LAIRA Interface: Received user query: {query}")
    lead = initialize_research_team()
    final_report = lead.process_query(query)
    logger.info("LAIRA Interface: Final report generated.")
    return final_report

def main():
    logger.info("Launching LAIRA Gradio interface...")
    interface = gr.Interface(
        fn=laira_interface,
        inputs=gr.components.Textbox(lines=2, placeholder="Enter your research query here..."),
        outputs="text",
        title="LAIRA - Langchain AI Research Assistants",
        description=(
            "Welcome to LAIRA. Enter your research query to trigger a conversation-based research flow "
            "between AI agents until a final report is produced."
        ),
        theme="default"
    )
    interface.launch()

if __name__ == "__main__":
    main()
