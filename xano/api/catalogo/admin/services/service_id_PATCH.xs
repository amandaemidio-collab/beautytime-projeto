// Updates service details without allowing the company or normalized key to be supplied.
query "admin/services/{service_id}" verb=PATCH {
  api_group = "Catalogo"
  auth = "user"

  input {
    int service_id
    text name? filters=trim
    int duration_minutes?
    int price_cents?
  }

  stack {
    function.run "Catalogo/authorize_admin" {
      input = {authenticated_user_id: $auth.id}
    } as $account_id
  
    db.query service {
      where = $db.service.id == $input.service_id && $db.service.account_id == $account_id
      return = {type: "single"}
    } as $service
  
    precondition ($service != null) {
      error_type = "notfound"
      error = "Service not found."
    }
  
    precondition ($input.name != null || $input.duration_minutes != null || $input.price_cents != null) {
      error_type = "inputerror"
      error = "At least one service field must be provided."
    }
  
    function.run "Catalogo/validate_service" {
      input = {
        name            : $input.name ?? $service.name
        duration_minutes: $input.duration_minutes ?? $service.duration_minutes
        price_cents     : $input.price_cents ?? $service.price_cents
      }
    } as $validated
  
    db.query service {
      where = $db.service.account_id == $account_id && $db.service.name_key == $validated.name_key && $db.service.id != $service.id
      return = {type: "single"}
    } as $existing_service
  
    precondition ($existing_service == null) {
      error_type = "inputerror"
      error = "service_name_taken"
    }
  
    db.edit service {
      field_name = "id"
      field_value = $service.id
      data = {
        name            : $validated.name
        name_key        : $validated.name_key
        duration_minutes: $validated.duration_minutes
        price_cents     : $validated.price_cents
      }
    } as $updated_service
  
    function.run "Getting Started Template/create_event_log" {
      input = {
        user_id   : $auth.id
        account_id: $account_id
        action    : "update_service"
        metadata  : {service_id: $updated_service.id}
      }
    } as $event_log
  }

  response = {
    id              : $updated_service.id
    name            : $updated_service.name
    duration_minutes: $updated_service.duration_minutes
    price_cents     : $updated_service.price_cents
    is_active       : $updated_service.is_active
  }

  guid = "_3OvTnqrGNwmUWA2pNzk59tbzV4"
}