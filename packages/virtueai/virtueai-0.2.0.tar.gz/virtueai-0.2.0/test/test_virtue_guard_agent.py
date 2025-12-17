import argparse
from re import S
from virtueai import VirtueAIModel, DatabricksDbModel
from openai import OpenAI
from virtueai.guard.virtue_guard_agent import VirtueGuardResponsesAgent
from mlflow.types.responses import ResponsesAgentRequest, ResponsesAgentResponse

def test_virtue_guard_agent(databricks_api_key: str, databricks_url: str, virtueai_api_key: str, safety_check_query: bool, safety_check_response: bool):
    
    messages = [{"role": "user", "content": "hi"}]
    

    databricks_client = OpenAI(
        api_key=databricks_api_key,
        base_url=databricks_url,
    )
    model = "databricks-meta-llama-3-1-8b-instruct"
    completion = databricks_client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=5,
    )
    assistant_output = completion.choices[0].message.content
    print(f"Assistant output: {assistant_output}")
    

    AGENT = VirtueGuardResponsesAgent(api_key=virtueai_api_key, safety_model=VirtueAIModel.VIRTUE_GUARD_TEXT_LITE)
    
    request = ResponsesAgentRequest(input=messages)

    response: ResponsesAgentResponse = AGENT.predict(request)
    print(f"Response: {response}")

    response.model_dump(exclude_none=True)
    print(f"Response: {response}")
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Databricks Guard")
    parser.add_argument("--databricks-api-key", required=True, help="Databricks API key")
    parser.add_argument("--databricks-url", required=True, help="Databricks URL")
    parser.add_argument("--virtueai-api-key", required=True, help="VirtueAI API key")
    parser.add_argument("--disable-safety-check-query", action="store_true", help="Safety check query")
    parser.add_argument("--disable-safety-check-response", action="store_true", help="Safety check response")
    args = parser.parse_args()

    # print(f"Safety check query: {not args.disable_safety_check_query}")
    # print(f"Safety check response: {not args.disable_safety_check_response}")

    test_virtue_guard_agent(
        databricks_api_key=args.databricks_api_key,
        databricks_url=args.databricks_url,
        virtueai_api_key=args.virtueai_api_key,
        safety_check_query=not args.disable_safety_check_query,
        safety_check_response=not args.disable_safety_check_response,
    )
