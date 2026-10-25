// Stores appointment details and the service values agreed at booking time.
table appointment {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
    int account_id {
      table = "account"
    }
    int client_id {
      table = "user"
    }
    int professional_id {
      table = "professional"
    }
    int service_id {
      table = "service"
    }
    timestamp starts_at
    timestamp ends_at
    enum status?="agendado" {
      values = ["agendado", "cancelado"]
    }
    bool is_late_cancellation?=false
    text service_name
    int service_duration_minutes
    int service_price_cents
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "account_id"}, {name: "starts_at"}]}
    {type: "btree", field: [{name: "client_id"}, {name: "starts_at"}]}
    {type: "btree", field: [{name: "professional_id"}, {name: "starts_at"}]}
    {type: "btree", field: [{name: "status"}, {name: "starts_at"}]}
  ]
  guid = "i3jQO2HdlO6WCjMWDpJsHVtLiBw"
}
