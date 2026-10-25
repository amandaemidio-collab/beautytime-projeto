// Activates or deactivates a service belonging to the authenticated administrator's company.
query "admin/services/{service_id}/status" verb=PATCH {
  api_group = "Catalogo"
  auth = "user"

  input {
    int service_id
    bool is_active
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
  
    db.edit service {
      field_name = "id"
      field_value = $service.id
      data = {is_active: $input.is_active}
    } as $updated_service
  
    function.run "Getting Started Template/create_event_log" {
      input = {
        user_id   : $auth.id
        account_id: $account_id
        action    : "set_service_status"
        metadata  : {
        service_id: $updated_service.id
        is_active : $updated_service.is_active
      }
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

  guid = "zXdLDPaeawXVbB0Vb7WqejD9NWw"
}