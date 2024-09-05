Feature: MTD Controller Management

Background:
    Given I have a running firewalld service
    Given I have a running docker service

    Scenario: Create a valid MTD
        When I create a MTDController with 60 duration, 15 lower and 15 upper
        Then the MTD should be created correctly
        When I close the MTD
        Then there should be no containers running
        And the firewall configuration should be the same as the start of the scenario

    Scenario: Create an ivalid MTD
        When I create a MTDController with 60 duration, 16 lower and 15 upper
        Then the MTD creation should fail

    Scenario: Run a MTD
        When I create a MTDController with 60 duration, 15 lower and 15 upper
        Then the MTD should be created correctly
        When the MTD is started
        Then the running should be successful
        When I close the MTD
        Then there should be no containers running
        And the firewall configuration should be the same as the start of the scenario

    Scenario: Stop a MTD during the run
        When I create a MTDController with 60 duration, 15 lower and 15 upper
        Then the MTD should be created correctly
        When the MTD is started asynchronously 
        And I press crtl+c
        Then the running should stop
        When I close the MTD
        Then there should be no containers running
        And the firewall configuration should be the same as the start of the scenario
