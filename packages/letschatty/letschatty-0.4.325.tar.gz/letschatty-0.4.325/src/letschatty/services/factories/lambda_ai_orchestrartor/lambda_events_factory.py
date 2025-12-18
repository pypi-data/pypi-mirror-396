
from letschatty.models import StrObjectId
from letschatty.models.ai_microservices.lambda_events import DoubleCheckerForIncomingMessagesAnswerCallbackEvent, DoubleCheckerForIncomingMessagesAnswerEvent, FixBuggedAiAgentsCallsInChatsEvent, GetChainOfThoughtsByChatIdEvent, GetChatWithPromptForFollowUpEvent, GetChatWithPromptForIncomingMessageEvent, QualityTestEventData, QualityTestsForUpdatedAIComponentEvent, QualityTestsForUpdatedAIComponentEventData, ManualTriggerEvent, CancelExecutionEvent, AssignAIAgentToChatEvent, RemoveAIAgentFromChatEvent, UpdateAIAgentModeInChatEvent, EscalateAIAgentInChatEvent, UnescalateAIAgentInChatEvent, SmartFollowUpDecisionOutputEvent
from letschatty.models.ai_microservices.lambda_invokation_types import InvokationType
from letschatty.models.ai_microservices import AllQualityTestEvent, AllQualityTestEventData, QualityTestEvent, QualityTestInteractionCallbackEvent, SmartTaggingCallbackEvent, QualityTestCallbackEvent, LambdaAiEvent, SmartTaggingEvent, SmartTaggingPromptEvent
from letschatty.models.base_models.ai_agent_component import AiAgentComponent
from letschatty.models.company.assets.ai_agents_v2.chat_example import ChatExample
from letschatty.models.company.assets.ai_agents_v2.chat_example_test import ChatExampleTestCase

class LambdaEventFactory:

    @staticmethod
    def instantiate_event(event_data: dict) -> LambdaAiEvent:
        event_type = event_data["type"]
        match event_type:
            case InvokationType.QUALITY_TEST_INTERACTION:
                return QualityTestInteractionCallbackEvent(**event_data)
            case InvokationType.SMART_TAGGING:
                return SmartTaggingEvent(**event_data)
            case InvokationType.SMART_TAGGING_CALLBACK:
                return SmartTaggingCallbackEvent(**event_data)
            case InvokationType.SINGLE_QUALITY_TEST:
                return QualityTestEvent(**event_data)
            case InvokationType.ALL_QUALITY_TEST:
                return AllQualityTestEvent(**event_data)
            case InvokationType.SINGLE_QUALITY_TEST_CALLBACK:
                return QualityTestCallbackEvent(**event_data)
            case InvokationType.SMART_TAGGING_PROMPT:
                return SmartTaggingPromptEvent(**event_data)
            case InvokationType.QUALITY_TESTS_FOR_UPDATED_AI_COMPONENT:
                return QualityTestsForUpdatedAIComponentEvent(**event_data)
            case InvokationType.FIX_BUGGED_AI_AGENTS_CALLS_IN_CHATS:
                return FixBuggedAiAgentsCallsInChatsEvent(**event_data)
            case InvokationType.DOUBLE_CHECKER_FOR_INCOMING_MESSAGES_ANSWER:
                return DoubleCheckerForIncomingMessagesAnswerEvent(**event_data)
            case InvokationType.DOUBLE_CHECKER_FOR_INCOMING_MESSAGES_ANSWER_CALLBACK:
                return DoubleCheckerForIncomingMessagesAnswerCallbackEvent(**event_data)
            case InvokationType.GET_CHAT_WITH_PROMPT_INCOMING_MESSAGE:
                return GetChatWithPromptForIncomingMessageEvent(**event_data)
            case InvokationType.GET_CHAT_WITH_PROMPT_FOLLOW_UP:
                return GetChatWithPromptForFollowUpEvent(**event_data)
            case InvokationType.MANUAL_TRIGGER:
                return ManualTriggerEvent(**event_data)
            case InvokationType.CANCEL_EXECUTION:
                return CancelExecutionEvent(**event_data)
            case InvokationType.ASSIGN_AI_AGENT_TO_CHAT:
                return AssignAIAgentToChatEvent(**event_data)
            case InvokationType.REMOVE_AI_AGENT_FROM_CHAT:
                return RemoveAIAgentFromChatEvent(**event_data)
            case InvokationType.UPDATE_AI_AGENT_MODE_IN_CHAT:
                return UpdateAIAgentModeInChatEvent(**event_data)
            case InvokationType.ESCALATE_AI_AGENT_IN_CHAT:
                return EscalateAIAgentInChatEvent(**event_data)
            case InvokationType.UNESCALATE_AI_AGENT_IN_CHAT:
                return UnescalateAIAgentInChatEvent(**event_data)
            case InvokationType.GET_CHAIN_OF_THOUGHTS_BY_CHAT_ID:
                return GetChainOfThoughtsByChatIdEvent(**event_data)
            case InvokationType.SMART_FOLLOW_UP_DECISION_OUTPUT:
                return SmartFollowUpDecisionOutputEvent(**event_data)

            case _:
                raise ValueError(f"Invalid event type: {event_type}")

    @staticmethod
    def create_quality_test_event_from_chat_example(chat_example: ChatExample) -> QualityTestEvent:
        """Create a quality test event from a test case"""
        return QualityTestEvent(
            type=InvokationType.SINGLE_QUALITY_TEST,
            data=QualityTestEventData(
                chat_example_id=chat_example.id,
                company_id=chat_example.company_id,
                ai_agent_id=chat_example.ai_agent_id_value
            )
        )

    @staticmethod
    def create_updated_ai_component_event_for_running_test_cases(ai_component: AiAgentComponent) -> QualityTestsForUpdatedAIComponentEvent:
        """Create an updated ai component event for running test cases"""
        return QualityTestsForUpdatedAIComponentEvent(
            type=InvokationType.QUALITY_TESTS_FOR_UPDATED_AI_COMPONENT,
            data=QualityTestsForUpdatedAIComponentEventData(company_id=ai_component.company_id, ai_component_id=ai_component.id, ai_component_type=ai_component.type)
        )

    @staticmethod
    def create_run_all_quality_tests_for_ai_agent(company_id: StrObjectId, ai_agent_id: StrObjectId) -> AllQualityTestEvent:
        """Create a all quality tests event for running all quality tests for an ai agent"""
        return AllQualityTestEvent(
            type=InvokationType.ALL_QUALITY_TEST,
            data=AllQualityTestEventData(company_id=company_id, ai_agent_id=ai_agent_id)
        )
