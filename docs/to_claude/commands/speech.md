<!-- ---
!-- Timestamp: 2026-02-08 15:51:42
!-- Author: ywatanabe
!-- File: /home/ywatanabe/.dotfiles/src/.claude/to_claude/commands/speak.md
!-- --- -->

## Speak Feedback Rules

### Backgrounds
The user has vulnerable eyes.

### Requests
Provide audio feedback via MCP tool `scitex - audio_speak` or `scitex - audio_speak_relay`
As well as audio feedback, please display the feedback in readable format of text as well.

### Rules

#### Concise
Transcription must be short, concise, and information-dense. No extra words, no long sentences, no storytelling.

#### Signature
Do not add signature unless explicitly requested.

#### Backend
~~Use `elevenlabs` with `x1.2` speed~~ -> Cancelled Elevenlabs subscription
Use `gtts` with `x1.5` speed

#### Repeat
When asked to speak consectively, it means the user is working for other tasks. Please just keep repeating your feedback until user respond. But again, your autonomous work is highly recommended without user confirmation.

#### Autonomous
Your autonomous work is quite powerful. Under your responsibility, please choose the best options and work autonomously without waiting for user's confirmation. Do not stand by. Proactively find what you contribute to the project and move to action.

### Formats

#### Progress Report - Next
```
Progress - Next: I will do XXX now.
```

#### Progress Report - Completion
```
Progress - Completion: I have done XXX.
```

#### Progress Report - Bug
```
Progress - Bug: : I found XXX in the codebase. I'm proceeding with fixing this.
```

#### Progress Report - Completion
```
Progress - Completion: I have done XXX. Next, I will move on working XXX.
```

#### Question - Choices:
```
Question - Choices: 1. XXX. 2. YYY. I'm proceeding with the option 1, which I believe the best.
```

#### Question - Open:
```
Question - Open: Could you clarify XXX?
```

<!-- EOF -->