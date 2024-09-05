Feature: Container Controller Management

  Background:
    Given I have a running docker service

  Scenario Outline: Create a valid container
    When I create a ContainerController with a <container> container
    Then the <container> container should be running
    When closing the ContainerController
    Then there should be no containers running

    Examples:
      | container |
      | nginx     |
      | httpd     |


  Scenario Outline: Remove a container after creating it
    When I create a ContainerController with a <container> container
    Then the <container> container should be running
    When I remove the <container> container
    Then the <container> container should not be running
    When closing the ContainerController
    Then there should be no containers running

    Examples:
      | container |
      | nginx     |
      | httpd     |

  Scenario Outline: Create two different containers
    When I create a ContainerController with a <first> container
    Then the <first> container should be running
    When I create a <second> container
    Then the <second> container should be running
    When closing the ContainerController
    Then there should be no containers running

    Examples:
      | first | second |
      | nginx | httpd  |
      | httpd | nginx  |

  Scenario Outline: Rotating containers
    When I create a ContainerController with a <first> container
    Then the <first> container should be running
    When I create a <second> container
    Then the <second> container should be running
    When I remove the <first> container
    Then the <first> container should not be running
    When closing the ContainerController
    Then there should be no containers running

    Examples:
      | first | second |
      | nginx | httpd  |
      | httpd | nginx  |


  Scenario Outline: Triying to create two equal containers
    When I create a ContainerController with a <first> container
    Then the <first> container should be running
    When I create a <second> container
    Then the <second> container should be running
    And the <first> container should not be running
    When closing the ContainerController
    Then there should be no containers running

    Examples:
      | first | second |
      | nginx | nginx  |
      | httpd | httpd  |

  Scenario Outline: Triying to remove a deleted container
    When I create a ContainerController with a <container> container
    Then the <container> container should be running
    When I remove the <container> container
    Then the <container> container should not be running
    When I remove the <container> container
    Then the <container> container should not be running
    When closing the ContainerController
    Then there should be no containers running

    Examples:
      | container |
      | nginx     |
      | httpd     |
