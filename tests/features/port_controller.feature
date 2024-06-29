Feature: PortController

  Background:
    Given I have a running firewalld service

  ### TESTING NORMAL FUNCTIONALITY ###

  Scenario Outline: Creating a PortController with a valid container
    Given the masquerade <masquerade>
    When I create a PortController with the <container_port> container port
    Then it should succeed
    And the masquerade should be enabled
    And the <container_port> port for the running container should be added
    When closing the controller
    Then the firewall configuration should be the same as the start of the scenario

    Examples:
      | container_port | masquerade |
      | NGINX          | 0          |
      | NGINX          | 1          |
      | HTTPD          | 0          |
      | HTTPD          | 1          |

  Scenario Outline: Creating a PortController and rotating once 
    Given the ports <nginx_udp>, <nginx_tcp>, <httpd_udp>, <httpd_tcp>
    When I create a PortController with the <container_port> container port
    Then it should succeed
    And the masquerade should be enabled
    And the <container_port> port for the running container should be added
    When rotating to <swap>
    Then it should succeed
    And the <swap> port for the running container should be added
    And the <container_port> port for the old container should be removed
    When closing the controller
    Then the firewall configuration should be the same as the start of the scenario
    
    # Masquerade not necessary to retest because its only modified in the creation and closing 
    Examples:
      | container_port | swap  | nginx_udp | nginx_tcp | httpd_udp | httpd_tcp |
      | NGINX          | HTTPD | 0         | 0         | 0         | 0         |
      | NGINX          | HTTPD | 0         | 0         | 0         | 1         |
      | NGINX          | HTTPD | 0         | 0         | 1         | 0         |
      | NGINX          | HTTPD | 0         | 0         | 1         | 1         |
      | NGINX          | HTTPD | 0         | 1         | 0         | 0         |
      | NGINX          | HTTPD | 0         | 1         | 0         | 1         |
      | NGINX          | HTTPD | 0         | 1         | 1         | 0         |
      | NGINX          | HTTPD | 0         | 1         | 1         | 1         |
      | NGINX          | HTTPD | 1         | 0         | 0         | 0         |
      | NGINX          | HTTPD | 1         | 0         | 0         | 1         |
      | NGINX          | HTTPD | 1         | 0         | 1         | 0         |
      | NGINX          | HTTPD | 1         | 0         | 1         | 1         |
      | NGINX          | HTTPD | 1         | 1         | 0         | 0         |
      | NGINX          | HTTPD | 1         | 1         | 0         | 1         |
      | NGINX          | HTTPD | 1         | 1         | 1         | 0         |
      | NGINX          | HTTPD | 1         | 1         | 1         | 1         |
      | HTTPD          | NGINX | 0         | 0         | 0         | 0         |
      | HTTPD          | NGINX | 0         | 0         | 0         | 1         |
      | HTTPD          | NGINX | 0         | 0         | 1         | 0         |
      | HTTPD          | NGINX | 0         | 0         | 1         | 1         |
      | HTTPD          | NGINX | 0         | 1         | 0         | 0         |
      | HTTPD          | NGINX | 0         | 1         | 0         | 1         |
      | HTTPD          | NGINX | 0         | 1         | 1         | 0         |
      | HTTPD          | NGINX | 0         | 1         | 1         | 1         |
      | HTTPD          | NGINX | 1         | 0         | 0         | 0         |
      | HTTPD          | NGINX | 1         | 0         | 0         | 1         |
      | HTTPD          | NGINX | 1         | 0         | 1         | 0         |
      | HTTPD          | NGINX | 1         | 0         | 1         | 1         |
      | HTTPD          | NGINX | 1         | 1         | 0         | 0         |
      | HTTPD          | NGINX | 1         | 1         | 0         | 1         |
      | HTTPD          | NGINX | 1         | 1         | 1         | 0         |
      | HTTPD          | NGINX | 1         | 1         | 1         | 1         |


  Scenario Outline: Creating a PortController and rotating twice 
    Given the ports <nginx_udp>, <nginx_tcp>, <httpd_udp>, <httpd_tcp>
    When I create a PortController with the <first> container port
    Then it should succeed
    And the masquerade should be enabled
    And the <first> port for the running container should be added
    When rotating to <second>
    Then it should succeed
    And the <second> port for the running container should be added
    And the <first> port for the old container should be removed
    When rotating to <first>
    Then it should succeed
    And the <first> port for the running container should be added
    And the <second> port for the old container should be removed
    When closing the controller
    Then the firewall configuration should be the same as the start of the scenario
    
    Examples:
      | first | second  | nginx_udp | nginx_tcp | httpd_udp | httpd_tcp |
      | NGINX | HTTPD   | 0         | 0         | 0         | 0         |
      | NGINX | HTTPD   | 0         | 0         | 0         | 1         |
      | NGINX | HTTPD   | 0         | 0         | 1         | 0         |
      | NGINX | HTTPD   | 0         | 0         | 1         | 1         |
      | NGINX | HTTPD   | 0         | 1         | 0         | 0         |
      | NGINX | HTTPD   | 0         | 1         | 0         | 1         |
      | NGINX | HTTPD   | 0         | 1         | 1         | 0         |
      | NGINX | HTTPD   | 0         | 1         | 1         | 1         |
      | NGINX | HTTPD   | 1         | 0         | 0         | 0         |
      | NGINX | HTTPD   | 1         | 0         | 0         | 1         |
      | NGINX | HTTPD   | 1         | 0         | 1         | 0         |
      | NGINX | HTTPD   | 1         | 0         | 1         | 1         |
      | NGINX | HTTPD   | 1         | 1         | 0         | 0         |
      | NGINX | HTTPD   | 1         | 1         | 0         | 1         |
      | NGINX | HTTPD   | 1         | 1         | 1         | 0         |
      | NGINX | HTTPD   | 1         | 1         | 1         | 1         |
      | HTTPD | NGINX   | 0         | 0         | 0         | 0         |
      | HTTPD | NGINX   | 0         | 0         | 0         | 1         |
      | HTTPD | NGINX   | 0         | 0         | 1         | 0         |
      | HTTPD | NGINX   | 0         | 0         | 1         | 1         |
      | HTTPD | NGINX   | 0         | 1         | 0         | 0         |
      | HTTPD | NGINX   | 0         | 1         | 0         | 1         |
      | HTTPD | NGINX   | 0         | 1         | 1         | 0         |
      | HTTPD | NGINX   | 0         | 1         | 1         | 1         |
      | HTTPD | NGINX   | 1         | 0         | 0         | 0         |
      | HTTPD | NGINX   | 1         | 0         | 0         | 1         |
      | HTTPD | NGINX   | 1         | 0         | 1         | 0         |
      | HTTPD | NGINX   | 1         | 0         | 1         | 1         |
      | HTTPD | NGINX   | 1         | 1         | 0         | 0         |
      | HTTPD | NGINX   | 1         | 1         | 0         | 1         |
      | HTTPD | NGINX   | 1         | 1         | 1         | 0         |
      | HTTPD | NGINX   | 1         | 1         | 1         | 1         |


  ### TESTING INVALID VALUES ###

  Scenario Outline: Creating a PortController with a nonexistent container
    Given the ports <nginx_udp>, <nginx_tcp>, <httpd_udp>, <httpd_tcp>
    When I create a PortController with the TOMCAT container port
    Then it should fail
    And the firewall configuration should be the same as the start of the scenario

  Examples:
    | nginx_udp | nginx_tcp | httpd_udp | httpd_tcp |
    | 0         | 0         | 0         | 0         |
    | 0         | 0         | 0         | 1         |
    | 0         | 0         | 1         | 0         |
    | 0         | 0         | 1         | 1         |
    | 0         | 1         | 0         | 0         |
    | 0         | 1         | 0         | 1         |
    | 0         | 1         | 1         | 0         |
    | 0         | 1         | 1         | 1         |
    | 1         | 0         | 0         | 0         |
    | 1         | 0         | 0         | 1         |
    | 1         | 0         | 1         | 0         |
    | 1         | 0         | 1         | 1         |
    | 1         | 1         | 0         | 0         |
    | 1         | 1         | 0         | 1         |
    | 1         | 1         | 1         | 0         |
    | 1         | 1         | 1         | 1         |


  ### TESTING EXTERNAL EVENTS ### 

  ### TBD