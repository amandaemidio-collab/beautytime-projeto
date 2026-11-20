// Updates editable salon details and records the change in the event log.
query "platform/accounts/{account_id}" verb=PATCH {
  api_group = "Platform"
  auth = "user"

  input {
    int account_id
    text name? filters=trim
    text description? filters=trim
    text location? filters=trim
  }

  stack {
    function.run "authorize_platform_admin" {
      input = {authenticated_user_id: $auth.id}
    } as $platform_admin_id

    db.get account {
      field_name = "id"
      field_value = $input.account_id
    } as $account

    precondition ($account != null) {
      error_type = "notfound"
      error = "Salon not found."
    }

    precondition ($input.name != null || $input.description != null || $input.location != null) {
      error_type = "inputerror"
      error = "At least one salon field must be provided."
    }

    precondition ($input.name == null || ($input.name|strlen) > 0) {
      error_type = "inputerror"
      error = "Salon name cannot be empty."
    }

    var $changed_fields {
      value = []
    }

    conditional {
      if ($input.name != null) {
        array.push $changed_fields { value = "name" }
      }
    }

    conditional {
      if ($input.description != null) {
        array.push $changed_fields { value = "description" }
      }
    }

    conditional {
      if ($input.location != null) {
        array.push $changed_fields { value = "location" }
      }
    }

    db.transaction {
      stack {
        db.edit account {
          field_name = "id"
          field_value = $account.id
          data = {
            name       : $input.name ?? $account.name
            description: $input.description ?? $account.description
            location   : $input.location ?? $account.location
          }
        } as $updated_account

        function.run "Getting Started Template/create_event_log" {
          input = {
            user_id   : $auth.id
            account_id: $account.id
            action    : "platform_update_account"
            metadata  : {
              changed_fields: $changed_fields
              before: {
                name: $account.name
                description: $account.description
                location: $account.location
              }
              after: {
                name: $updated_account.name
                description: $updated_account.description
                location: $updated_account.location
              }
            }
          }
        } as $event_log
      }
    }
  }

  response = {
    id: $updated_account.id
    name: $updated_account.name
    public_identifier: $updated_account.public_identifier
    description: $updated_account.description
    location: $updated_account.location
  }
  guid = "AtJ5Uw-fn03RPAmw0TbU5jSUqtk"
}
