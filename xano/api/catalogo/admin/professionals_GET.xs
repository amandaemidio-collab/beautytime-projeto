// Lists professionals and service associations for the authenticated company.
query "admin/professionals" verb=GET {
  api_group = "Catalogo"
  auth = "user"

  input {
  }

  stack {
    function.run "Catalogo/authorize_admin" {
      input = {authenticated_user_id: $auth.id}
    } as $account_id

    db.query professional {
      where = $db.professional.account_id == $account_id
      sort = {name: "asc"}
      return = {type: "list"}
    } as $professionals

    db.query service {
      where = $db.service.account_id == $account_id && $db.service.is_active == true
      sort = {name: "asc"}
      return = {type: "list"}
    } as $services

    db.query professional_service {
      join = {
        professional: {
          table: "professional",
          type: "inner",
          where: $db.professional_service.professional_id == $db.professional.id
        }
        service: {
          table: "service",
          type: "inner",
          where: $db.professional_service.service_id == $db.service.id
        }
      }
      eval = {
        service_name: $db.service.name,
        service_is_active: $db.service.is_active
      }
      where = $db.professional.account_id == $account_id
      sort = {professional_id: "asc"}
      return = {type: "list"}
    } as $service_associations
  }

  response = {
    professionals: ```
      $professionals|map:{
        id: $$.id,
        name: $$.name,
        is_active: $$.is_active
      }
      ```
    services: ```
      $services|map:{
        id: $$.id,
        name: $$.name
      }
      ```
    service_associations: ```
      $service_associations|map:{
        professional_id: $$.professional_id,
        service_id: $$.service_id,
        service_name: $$.service_name,
        service_is_active: $$.service_is_active
      }
      ```
  }
  guid = "9QjWzcwMtfblJRJ08v-LoDkxnt8"
}
