Feature: Retrieving actor information

    Background:
        Given A new user called "Alice"

    Scenario: Can retrieve information
        When The actor information of "Alice" is retrieved
        Then The result has the name "Alice"

    Scenario: Name gets updated
        Given The actor information of "Alice" was retrieved
        Given "Alice" renames herself "Bob"
        When The actor information of "Alice" is retrieved
        Then The result has the name "Bob"

    Scenario: Deletes herself
        Given The actor information of "Alice" was retrieved
        When "Alice" deletes herself
        And The actor information of "Alice" is retrieved
        Then No result is returned