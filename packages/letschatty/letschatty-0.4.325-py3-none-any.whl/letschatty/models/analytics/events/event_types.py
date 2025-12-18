from enum import StrEnum

class EventType(StrEnum):
    ##CHAT EVENTS
    CHAT_CREATED = "chat.created"
    CHAT_STATUS_UPDATED = "chat.status_updated"
    CHAT_DELETED = "chat.deleted"
    #TAGS
    TAG_ASSIGNED = "chat.tag.assigned"
    TAG_REMOVED = "chat.tag.removed"
    #CHATTY AI AGENTS
    AI_AGENT_ASSIGNED_TO_CHAT = "chat.chatty_ai_agent.assigned_to_chat"
    AI_AGENT_REMOVED_FROM_CHAT = "chat.chatty_ai_agent.removed_from_chat"
    AI_AGENT_UPDATED_ON_CHAT = "chat.chatty_ai_agent.updated_on_chat"

    #CHATTY AI AGENT EXECUTION EVENTS - 3-level hierarchy for execution tracking
    # Pattern: chatty_ai_agent_in_chat.{operation}.{detail}
    # Note: Execution events are already chat-scoped via CustomerEventData

    # TRIGGER EVENTS - What initiates AI agent processing
    CHATTY_AI_AGENT_IN_CHAT_TRIGGER_USER_MESSAGE = "chatty_ai_agent_in_chat.trigger.user_message"
    CHATTY_AI_AGENT_IN_CHAT_TRIGGER_FOLLOW_UP = "chatty_ai_agent_in_chat.trigger.follow_up"
    CHATTY_AI_AGENT_IN_CHAT_TRIGGER_MANUAL = "chatty_ai_agent_in_chat.trigger.manual"
    CHATTY_AI_AGENT_IN_CHAT_TRIGGER_RETRY = "chatty_ai_agent_in_chat.trigger.retry"

    # STATE EVENTS - AI agent state changes
    CHATTY_AI_AGENT_IN_CHAT_STATE_PROCESSING_STARTED = "chatty_ai_agent_in_chat.state.processing_started"
    CHATTY_AI_AGENT_IN_CHAT_STATE_CALL_STARTED = "chatty_ai_agent_in_chat.state.call_started"
    CHATTY_AI_AGENT_IN_CHAT_STATE_ESCALATED = "chatty_ai_agent_in_chat.state.escalated"
    CHATTY_AI_AGENT_IN_CHAT_STATE_UNESCALATED = "chatty_ai_agent_in_chat.state.unescalated"

    # CALL EVENTS - Outbound calls to services
    CHATTY_AI_AGENT_IN_CHAT_CALL_GET_CHAT_WITH_PROMPT = "chatty_ai_agent_in_chat.call.get_chat_with_prompt"
    CHATTY_AI_AGENT_IN_CHAT_CALL_TAGGER = "chatty_ai_agent_in_chat.call.tagger"
    CHATTY_AI_AGENT_IN_CHAT_CALL_DOUBLE_CHECKER = "chatty_ai_agent_in_chat.call.double_checker"
    CHATTY_AI_AGENT_IN_CHAT_CALL_DEBUGGER = "chatty_ai_agent_in_chat.call.debugger"

    # CALLBACK EVENTS - Responses received from services
    CHATTY_AI_AGENT_IN_CHAT_CALLBACK_GET_CHAT_WITH_PROMPT = "chatty_ai_agent_in_chat.callback.get_chat_with_prompt"
    CHATTY_AI_AGENT_IN_CHAT_CALLBACK_TAGGER = "chatty_ai_agent_in_chat.callback.tagger"
    CHATTY_AI_AGENT_IN_CHAT_CALLBACK_DOUBLE_CHECKER = "chatty_ai_agent_in_chat.callback.double_checker"
    CHATTY_AI_AGENT_IN_CHAT_CALLBACK_OUTPUT_RECEIVED = "chatty_ai_agent_in_chat.callback.output_received"

    # DECISION EVENTS - AI agent decisions and actions
    CHATTY_AI_AGENT_IN_CHAT_DECISION_SEND = "chatty_ai_agent_in_chat.decision.send"
    CHATTY_AI_AGENT_IN_CHAT_DECISION_SUGGEST = "chatty_ai_agent_in_chat.decision.suggest"
    CHATTY_AI_AGENT_IN_CHAT_DECISION_ESCALATE = "chatty_ai_agent_in_chat.decision.escalate"
    CHATTY_AI_AGENT_IN_CHAT_DECISION_SKIP = "chatty_ai_agent_in_chat.decision.skip"
    CHATTY_AI_AGENT_IN_CHAT_DECISION_SENT_TO_API = "chatty_ai_agent_in_chat.decision.sent_to_api"
    CHATTY_AI_AGENT_IN_CHAT_DECISION_COMPLETED = "chatty_ai_agent_in_chat.decision.completed"

    # ERROR EVENTS - Failures and cancellations
    CHATTY_AI_AGENT_IN_CHAT_ERROR_CALL_FAILED = "chatty_ai_agent_in_chat.error.call_failed"
    CHATTY_AI_AGENT_IN_CHAT_ERROR_CALL_CANCELLED = "chatty_ai_agent_in_chat.error.call_cancelled"
    CHATTY_AI_AGENT_IN_CHAT_ERROR_VALIDATION_FAILED = "chatty_ai_agent_in_chat.error.validation_failed"

    # RATING EVENTS - User feedback
    CHATTY_AI_AGENT_IN_CHAT_RATING_RECEIVED = "chatty_ai_agent_in_chat.rating.received"

    #PRODUCTS
    PRODUCT_ASSIGNED = "chat.product.assigned"
    PRODUCT_REMOVED = "chat.product.removed"
    #SALES
    SALE_CREATED = "chat.sale.created"
    SALE_UPDATED = "chat.sale.updated"
    SALE_DELETED = "chat.sale.deleted"
    #HIGHLIGHTS
    HIGHLIGHT_CREATED = "chat.highlight.created"
    HIGHLIGHT_UPDATED = "chat.highlight.updated"
    HIGHLIGHT_DELETED = "chat.highlight.deleted"
    #MESSAGES
    MESSAGE_RECEIVED = "chat.message.received"
    MESSAGE_SENT = "chat.message.sent"
    MESSAGE_STATUS_UPDATED = "chat.message.status_updated"
    #CONTACT POINTS
    CONTACT_POINT_CREATED = "chat.contact_point.created"
    CONTACT_POINT_UPDATED = "chat.contact_point.updated"
    CONTACT_POINT_DELETED = "chat.contact_point.deleted"
    #WORKFLOWS
    WORKFLOW_ASSIGNED = "chat.workflow.assigned"
    WORKFLOW_REMOVED = "chat.workflow.removed"
    WORKFLOW_STATUS_UPDATED = "chat.workflow.status_updated"
    #QUALITY SCORING
    GOOD_QUALITY_SCORE_ASSIGNED = "chat.quality_score.good"
    BAD_QUALITY_SCORE_ASSIGNED = "chat.quality_score.bad"
    NEUTRAL_QUALITY_SCORE_ASSIGNED = "chat.quality_score.neutral"
    #CONTINUOUS CONVERSATION
    CONTINUOUS_CONVERSATION_CREATED = "chat.continuous_conversation.created"
    CONTINUOUS_CONVERSATION_UPDATED = "chat.continuous_conversation.updated"
    #FUNNEL STAGES
    # Funnel-level events
    CHAT_FUNNEL_STARTED = "chat.funnel.started"  # New
    CHAT_FUNNEL_UPDATED = "chat.funnel.updated"
    CHAT_FUNNEL_COMPLETED = "chat.funnel.completed"
    CHAT_FUNNEL_ABANDONED = "chat.funnel.abandoned"

    #BUSINESS AREAS
    BUSINESS_AREA_ASSIGNED = "chat.business_area.assigned"
    BUSINESS_AREA_REMOVED = "chat.business_area.removed"
    ##COMPANY EVENTS
    COMPANY_CREATED = "company.created"
    COMPANY_UPDATED = "company.updated"
    COMPANY_DELETED = "company.deleted"
    #PRODUCTS
    PRODUCT_CREATED = "company.product.created"
    PRODUCT_UPDATED = "company.product.updated"
    PRODUCT_DELETED = "company.product.deleted"
    #CHATTY AI AGENTS
    CHATTY_AI_AGENT_CREATED = "company.chatty_ai_agent.created"
    CHATTY_AI_AGENT_UPDATED = "company.chatty_ai_agent.updated"
    CHATTY_AI_AGENT_DELETED = "company.chatty_ai_agent.deleted"
    #AI COMPONENTS
    AI_COMPONENT_CREATED = "company.ai_component.created"
    AI_COMPONENT_UPDATED = "company.ai_component.updated"
    AI_COMPONENT_DELETED = "company.ai_component.deleted"
    #SOURCES
    SOURCE_CREATED = "company.source.created"
    SOURCE_UPDATED = "company.source.updated"
    SOURCE_DELETED = "company.source.deleted"
    #TAGS
    TAG_CREATED = "company.tag.created"
    TAG_UPDATED = "company.tag.updated"
    TAG_DELETED = "company.tag.deleted"
    #TOPICS
    TOPIC_CREATED = "company.topic.created"
    TOPIC_UPDATED = "company.topic.updated"
    TOPIC_DELETED = "company.topic.deleted"
    #FAST ANSWERS
    FAST_ANSWER_CREATED = "company.fast_answer.created"
    FAST_ANSWER_UPDATED = "company.fast_answer.updated"
    FAST_ANSWER_DELETED = "company.fast_answer.deleted"
    #FUNNEL STAGES
    FUNNEL_CREATED = "company.funnel.created"
    FUNNEL_UPDATED = "company.funnel.updated"
    FUNNEL_DELETED = "company.funnel.deleted"
    FUNNEL_STAGE_CREATED = "company.funnel_stage.created"
    FUNNEL_STAGE_UPDATED = "company.funnel_stage.updated"
    FUNNEL_STAGE_DELETED = "company.funnel_stage.deleted"
    #BUSINESS AREA
    BUSINESS_AREA_CREATED = "company.business_area.created"
    BUSINESS_AREA_UPDATED = "company.business_area.updated"
    BUSINESS_AREA_DELETED = "company.business_area.deleted"
    #WORKFLOWS
    WORKFLOW_CREATED = "company.workflow.created"
    WORKFLOW_UPDATED = "company.workflow.updated"
    WORKFLOW_DELETED = "company.workflow.deleted"
    #AGENTS
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_LOGGED_IN = "user.logged_in"
    USER_LOGGED_OUT = "user.logged_out"
    USER_STATUS_UPDATED = "user.status_updated"
    USER_ASSIGNED_AREA = "user.assigned_area"
    USER_UNASSIGNED_AREA = "user.unassigned_area"
    USER_ASSIGNED_FUNNEL = "user.assigned_funnel"
    USER_UNASSIGNED_FUNNEL = "user.unassigned_funnel"
    #TEMPLATE CAMPAIGNS
    TEMPLATE_CAMPAIGN_CREATED = "company.template_campaign.created"
    TEMPLATE_CAMPAIGN_UPDATED = "company.template_campaign.updated"
    TEMPLATE_CAMPAIGN_DELETED = "company.template_campaign.deleted"
    #FILTER CRITERIA
    FILTER_CRITERIA_CREATED = "company.filter_criteria.created"
    FILTER_CRITERIA_UPDATED = "company.filter_criteria.updated"
    FILTER_CRITERIA_DELETED = "company.filter_criteria.deleted"
    #FORM FIELDS
    FORM_FIELD_CREATED = "company.form_field.created"
    FORM_FIELD_UPDATED = "company.form_field.updated"
    FORM_FIELD_DELETED = "company.form_field.deleted"
