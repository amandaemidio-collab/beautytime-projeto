// Lists bookable companies with only public account and active service fields.
query "public/accounts" verb=GET {
  api_group = "Members & Accounts"

  input {
    text search? filters=trim
    text service? filters=trim
  }

  stack {
    db.query professional_service {
      join = {
        service: {
          table: "service",
          type: "inner",
          where: $db.professional_service.service_id == $db.service.id
        }
        professional: {
          table: "professional",
          type: "inner",
          where: $db.professional_service.professional_id == $db.professional.id
        }
        account: {
          table: "account",
          type: "inner",
          where: $db.service.account_id == $db.account.id
        }
      }
      eval = {
        account_id: $db.account.id,
        name: $db.account.name,
        description: $db.account.description,
        location: $db.account.location,
        public_identifier: $db.account.public_identifier
      }
      where = $db.service.is_active == true && $db.professional.is_active == true && $db.service.account_id == $db.professional.account_id
      return = {type: "list"}
    } as $bookable_links

    var $account_ids {
      value = ($bookable_links|map:$$.account_id)|unique
    }

    var $results {
      value = []
    }

    foreach ($account_ids) {
      each as $account_id {
        var $account {
          value = ($bookable_links|filter:$$.account_id == $account_id)|first
        }

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
          where = $db.service.account_id == $account_id && $db.service.is_active == true
          sort = {name: "asc"}
          return = {type: "list"}
        } as $services

        var $matches_service {
          value = $input.service == null || ($input.service|strlen) == 0
        }

        conditional {
          if (!$matches_service) {
            foreach ($services) {
              each as $service_item {
                conditional {
                  if (($service_item.name|to_lower)|contains:($input.service|to_lower)) {
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
            var $public_services {
              value = []
            }

            foreach ($services) {
              each as $service_item {
                array.push $public_services {
                  value = {
                    name: $service_item.name,
                    duration_minutes: $service_item.duration_minutes,
                    price_cents: $service_item.price_cents
                  }
                }
              }
            }

            array.push $results {
              value = {
                name: $account.name,
                description: $account.description,
                location: $account.location,
                public_identifier: $account.public_identifier,
                services: $public_services
              }
            }
          }
        }
      }
    }
  }

  response = $results|sort:"name":"itext":true
  guid = "lhWPTUITchUE5Jt4VdKVNfhsB5Q"
}
