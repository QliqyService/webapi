from enum import IntEnum


class BaseExceptionCode(IntEnum):
    """Enum for Base Exception Codes."""

    pass


class QABaseExceptionCode(BaseExceptionCode):
    """Enum for QA Base Exception Codes."""

    NOT_EMPTY = 100_001  # QA base is not empty
    UPLOAD_FILE_DECODED_ERROR = 100_002  # Error while decoding the uploaded file
    UPLOAD_FILE_EMPTY = 100_003  # Empty file uploaded
    UPLOAD_FILE_EMPTY_ANSWER = 100_004  # Empty answer in the uploaded file
    UPLOAD_FILE_EMPTY_QUESTION = 100_005  # Empty question in the uploaded file
    DUPLICATE_QUESTION = 100_006  # Duplicate question in the uploaded file
    LOCKED = 100_007  # QA base is locked
    NOT_AVAILABLE_FOR_SYNC = 100_008  # QA base is not available for sync
    BLOCK_NOT_FOUND = 100_009  # QA block not found
    BASE_NOT_FOUND = 100_010  # QA base not found


class ChatLabelsExceptionCode(BaseExceptionCode):
    """Enum for Chat Label Exception Codes."""

    NOT_FOUND = 101_001  # Chat Label not found
    ALREADY_APPLIED = 101_002  # Chat Label already applied


class ProjectLabelsExceptionCode(BaseExceptionCode):
    """Enum for Project Labels Exception Codes."""

    NOT_FOUND = 102_001  # Project Label not found
    UPDATE_DATA_IS_EMPTY = 102_003  # Update data is empty
    USE_IN_CONVERSION = 102_004  # Project Label is used in conversion


class OperatorTagsExceptionCode(BaseExceptionCode):
    """Enum for Operator Tags Exception Codes."""

    NOT_FOUND = 103_001  # Operator Tag not found
    NAME_ALREADY_EXISTS = 103_002  # Operator Tag name already exists
    APPLIED_TO_OPERATOR = 103_003  # Operator Tag already applied to operator
    OPERATOR_NOT_FOUND = 103_004  # Operator not found
    ALREADY_APPLIED = 103_005  # Operator Tag already applied
    APPLIED_NOT_FOUND = 103_006  # Operator Tag applied not found


class UsersExceptionCode(BaseExceptionCode):
    """Enum for Users Exception Codes."""

    UNKNOWN = 104_000  # Unknown error
    NOT_FOUND = 104_001  # User not found
    EMAIL_ALREADY_EXISTS = 104_002  # Email already exists
    PHONE_ALREADY_EXISTS = 104_003  # Phone already exists
    INCORRECT_DEFAULT_AVATAR = 104_004  # Incorrect default avatar


class SettingsSystemMessagesExceptionCode(BaseExceptionCode):
    """Enum for Settings System Messages Exception Codes."""

    UNKNOWN = 105_000  # Unknown error
    ALREADY_EXISTS = 105_001  # System message already exists
    NOT_FOUND = 105_002  # System message not found
    SOURCE_NOT_SUPPORTED = 105_003  # Source not supported


class AuthExceptionCode(BaseExceptionCode):
    """Enum for Auth Exception Codes."""

    UNKNOWN = 106_000  # Unknown error
    BAD_CREDENTIALS = 106_001  # Bad credentials
    INVALID_PASSWORD = 106_002  # Invalid password
    RESET_PASSWORD_BAD_TOKEN = 106_003  # Reset password bad token
    RESET_PASSWORD_INVALID_PASSWORD = 106_004  # Reset password invalid password
    VERIFY_USER_BAD_TOKEN = 106_005  # Verify user bad token
    USER_ALREADY_VERIFIED = 106_006  # Verify user already verified


class OperatorsExceptionCode(BaseExceptionCode):
    """Enum for Operators Exception Codes."""

    UNKNOWN = 107_000  # Unknown error
    NOT_FOUND = 107_001  # Operator not found
    DEACTIVATED = 107_002  # Operator deactivated or already deactivated
    USER_EMAIL_NOT_FOUND = 107_003  # User email not found
    TOO_MANY_OPERATORS = 107_003  # Too many operators in project
    ALREADY_EXISTS = 107_004  # Operator already exists


class ProjectInvitationExceptionCode(BaseExceptionCode):
    """Enum for Project Invitation Exception Codes."""

    UNKNOWN = 108_000  # Unknown error
    EMPLOYEE_ALREADY_EXISTS = 108_001  # User already exists
    INVITATION_ALREADY_EXISTS = 108_002  # Invitation already exists
    LIMIT_OF_EMPLOYEES_EXCEEDED = 108_003  # Limit of employees exceeded
    TOKEN_EXPIRED = 108_004  # Token expired
    NOT_FOUND = 108_005  # Invitation not found
    UNSUPPORTED_METHOD = 108_006  # Unsupported method
    UNSUPPORTED_FOR_RESEND = 108_007  # Unsupported for resend
    UNSUPPORTED_FOR_RESEND_MESSAGE = 108_008  # Unsupported for resend message


class ProjectTriggerExceptionCode(BaseExceptionCode):
    """Enum for Project Trigger Exception Codes."""

    UNKNOWN = 109_000  # Unknown error
    NAME_ALREADY_EXISTS = 109_001  # Trigger name already exists
    NOT_FOUND = 109_002  # Trigger not found
    LOG_NOT_FOUND = 109_003  # Trigger log not found
    ALREADY_EXISTS = 109_004  # Trigger already exists


class ProjectAuthExceptionCode(BaseExceptionCode):
    """Enum for Project Auth Exception Codes."""

    UNKNOWN = 110_000  # Unknown error
    UNSUPPORTED_AUTH_TYPE = 110_001  # Unsupported authentication type
    UNAUTHORIZED = 110_002  # Unauthorized
    UNSUPPORTED_EMPLOYER_ROLE = 110_003  # Unsupported employer role
    INVALID_API_KEY = 110_004  # Invalid API key


class SettingsChatsExceptionCode(BaseExceptionCode):
    """Enum for Chat Settings Exception Codes."""

    # QueSmart routing can't be enabled if operator auto-assign is disabled
    ROUTING_REQUIRES_AUTO_ASSIGN_ENABLED = 111_00
    # QueSmart routing rules cannot be modified or their state changed if operator auto-assign is disabled
    ROUTING_RULE_MODIFICATION_REQUIRES_AUTO_ASSIGN_ENABLED = 112_00
    RESPONSE_TIME_EXCEEDS_INACTIVITY_TIME = (
        111_001  # The maximum response time to the client message cannot be greater than the session inactivity time.
    )


class SettingsQueSmartTagsExceptionCode(BaseExceptionCode):
    """Enum for QueSmart Tags Settings Exception Codes."""

    TAG_NOT_FOUND_IN_PROJECT = 113_000  # Client or Session Tag not found in project
    UNKNOWN_ROUTING_RULE_TAG_TYPE = 113_001  # Unknown tag type provided for a routing rule condition
    ROUTING_RULE_NOT_FOUND = 113_002  # Routing rule not found
    DEFAULT_ROUTING_RULE_ALREADY_EXISTS = 113_003  # Default routing rule already exists
    OPERATOR_GROUP_ROUTING_RULE_ALREADY_EXISTS = 113_004  # Routing rule for operator group already exists
    DUPLICATE_TAG_CONDITION_IN_RULE = 113_005  # Duplicate tag conditions (tag_id, tag_type) in rule update


class SettingsQueSmartTagsCrudExceptionCode(BaseExceptionCode):
    """Enum for QueSmart Tags CRUD operations Exception Codes (client and session tags)."""

    # Client Tag errors
    CHAT_TAG_NOT_FOUND = 114_000  # Chat tag not found in project
    CHAT_TAG_NAME_ALREADY_EXISTS = 114_001  # Chat tag with this name already exists in project

    # Session Tag errors
    SESSION_TAG_NOT_FOUND = 114_002  # Session tag not found in project
    SESSION_TAG_NAME_ALREADY_EXISTS = 114_003  # Session tag with this name already exists in project
    SESSION_TAG_CONDITION_ALREADY_EXISTS = 114_004  # Session tag with this condition already exists in project


class ProjectEmbedExceptionCode(BaseExceptionCode):
    """Enum for Project Embed Exception Codes."""

    UNKNOWN = 115_000  # Unknown error
    EMPLOYER_NOT_FOUND = 115_001  # Employer not found
    CHAT_NOT_FOUND = 115_002  # Chat not found
    NO_RIGHTS = 115_003  # No rights to generate embed
    EMPLOYER_ROLE_NOT_SUPPORTED = 115_004  # Employer role not supported


class QualityControlExceptionCode(BaseExceptionCode):
    """Enum for Quality Control Exception Codes."""

    UNKNOWN = 116_000  # Unknown error
    CLASSIFIER_NAME_ALREADY_EXISTS = 116_001  # Classifier with this name already exists in the project
    CLASSIFIER_GROUP_NOT_FOUND = 116_002  # Classifier group not found
    CLASSIFIER_NOT_FOUND = 116_003  # Classifier not found
    CLASSIFIER_ALREADY_DISABLED = 116_004  # Classifier already disabled
    CLASSIFIER_ALREADY_ENABLED = 116_005  # Classifier already enabled
    CLASSIFIER_GROUP_NAME_ALREADY_EXISTS = 116_006  # Classifier group with this name already exists in the project
    CLASSIFIER_GROUP_CANNOT_BE_DELETED = 116_007  # Classifier group cannot be deleted because it has classifiers
    CLASSIFIER_GROUPS_NOT_FOUND = 116_008  # Classifier groups not found
    CLASSIFIER_GROUP_CANNOT_BE_UPDATED = 116_009  # Classifier group cannot be updated
