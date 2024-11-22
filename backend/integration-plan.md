# Integration plan

Plan for how we merge it all together

Backend:

- keeps track of what meeting it is processing (needs to receive the meeting link)

## Remaining NLP work

### During the start of the conversation

Task: Check that the host has covered all the topics

- put the sample from FOE in the system prompt
- monitor the transcript from the host to see if they have covered all the topics

Possible action:
- Remind them about something they forgot

### During the goal-finding part of the session

Tasks:
- monitor the transcript and compare against expected
- At the end summarise the goals of the group

Possible action:
- Remind them about something they forgot

Action at the end:
- Send message

Need:

### During the main phase of the conversation

For each action type that is possible we need:

- Trigger examples (2-3) of what types of messages during the conversation should trigger that action.
- A description of the goal when taking this action (1 short paragraph) [This will be used as the system prompt]
- Output examples (2-3) of what a good response/suggestion
