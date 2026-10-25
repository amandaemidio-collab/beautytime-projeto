// Lists companies that accept bookings: an active service linked to an active professional of the same company.
query "companies/public" verb=GET {
  api_group = "Members & Accounts"

  input {
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
        company_id: $db.account.id,
        company_name: $db.account.name,
        company_identifier: $db.account.public_identifier
      }
      where = $db.service.is_active == true && $db.professional.is_active == true && $db.service.account_id == $db.professional.account_id
      return = {type: "list"}
    } as $links

    var $company_ids {
      value = ($links|map:$$.company_id)|unique
    }

    var $companies {
      value = []
    }

    foreach ($company_ids) {
      each as $company_id {
        var $link {
          value = ($links|filter:$$.company_id == $company_id)|first
        }

        array.push $companies {
          value = {
            name: $link.company_name
            public_identifier: $link.company_identifier
          }
        }
      }
    }
  }

  response = $companies|sort:"name":"itext":true
  guid = "gqYT058opJ9UW-XmID3wmZNgwds"
}
