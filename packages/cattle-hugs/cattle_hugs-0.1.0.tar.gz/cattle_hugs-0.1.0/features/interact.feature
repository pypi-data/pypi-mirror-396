Feature: Interactions

    Background:
        Given A new user called "Alice"
        And An ActivityPub object
        And "Alice" fetches the ActivityPub object

    Scenario:
        When "Alice" replies to the ActivityPub object with "Good post!"
        Then one get the interactions for the ActivityPub object
        And the interactions contains "Good post!"

    Scenario:
        Given "Alice" replied to the ActivityPub object with "Good post!"
        When "Alice" updates her reply with "Better post!"
        Then one get the interactions for the ActivityPub object
        And the interactions contains "Better post!"

    Scenario:
        Given "Alice" replied to the ActivityPub object with "Good post!"
        When "Alice" deletes her reply to the ActivityPub object
        Then one get the interactions for the ActivityPub object
        And the interactions does not contain "Good post!"

    Scenario:
        When "Alice" likes the ActivityPub object
        Then one get the interactions for the ActivityPub object
        And the number of "likes" in the interactions is "1"

    Scenario:
        When "Alice" announces the ActivityPub object
        Then one get the interactions for the ActivityPub object
        And the number of "shares" in the interactions is "1"