// Lists salons with optional name and active-service filters and record counts.
query "platform/accounts" verb=GET {
  api_group = "Platform"
  auth = "user"

  input {
    text search? filters=trim
    text service? filters=trim
  }

  stack {
    function.run "authorize_platform_admin" {
      input = {authenticated_user_id: $auth.id}
    } as $platform_admin_id

    db.query account {
      sort = {name: "asc"}
      return = {type: "list"}
    } as $accounts

    var $results {
      value = []
    }

    foreach ($accounts) {
      each as $account {
        var $matches_name {
          value = true
        }

        conditional {
          if ($input.search != null && ($input.search|strlen) > 0) {
            var.update $matches_name {
              value = ($account.name|to_lower)|contains:($input.search|to_lower)
            }
          }
        }

        db.query service {
          where = $db.service.account_id == $account.id
          return = {type: "list"}
        } as $services

        var $matches_service {
          value = ($input.service == null || ($input.service|strlen) == 0)
        }

        conditional {
          if (!$matches_service) {
            foreach ($services) {
              each as $service_item {
                conditional {
                  if ($service_item.is_active == true && (($service_item.name|to_lower)|contains:($input.service|to_lower))) {
                    var.update $matches_service {
                      value = true
                    }
                  }
                }
              }
            }
          }
        }

        conditional {
          if ($matches_name && $matches_service) {
            db.query professional {
              where = $db.professional.account_id == $account.id
              return = {type: "count"}
            } as $professional_count

            db.query appointment {
              where = $db.appointment.account_id == $account.id
              return = {type: "count"}
            } as $appointment_count

            array.push $results {
              value = {
                id: $account.id
                name: $account.name
                public_identifier: $account.public_identifier
                description: $account.description
                location: $account.location
                service_count: $services|count
                professional_count: $professional_count
                appointment_count: $appointment_count
              }
            }
          }
        }
      }
    }
  }

  response = $results
  guid = "pIIxHLA1SRLXax5Hn-bGAcClybE"
}
