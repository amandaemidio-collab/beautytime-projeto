// Creates an active service for the authenticated administrator's company.
query "admin/services" verb=POST {
  api_group = "Catalogo"
  auth = "user"

  input {
    text name filters=trim
    int duration_minutes
    int price_cents
  }

  stack {
    function.run "Catalogo/authorize_admin" {
      input = {authenticated_user_id: $auth.id}
    } as $account_id
  
    function.run "Catalogo/validate_service" {
      input = {
        name            : $input.name
        duration_minutes: $input.duration_minutes
        price_cents     : $input.price_cents
      }
    } as $validated
  
    db.query service {
      where = $db.service.account_id == $account_id && $db.service.name_key == $validated.name_key
      return = {type: "single"}
    } as $existing_service
  
    precondition ($existing_service == null) {
      error_type = "inputerror"
      error = "service_name_taken"
    }
  
    db.add service {
      data = {
        account_id      : $account_id
        name            : $validated.name
        name_key        : $validated.name_key
        duration_minutes: $validated.duration_minutes
        price_cents     : $validated.price_cents
        is_active       : true
      }
    } as $service
  
    function.run "Getting Started Template/create_event_log" {
      input = {
        user_id   : $auth.id
        account_id: $account_id
        action    : "create_service"
        metadata  : {service_id: $service.id}
      }
    } as $event_log
  }

  response = {
    id              : $service.id
    name            : $service.name
    duration_minutes: $service.duration_minutes
    price_cents     : $service.price_cents
    is_active       : $service.is_active
  }

  guid = "UXK6TeoRmaNcELhS7ogSFVjC0NY"
}