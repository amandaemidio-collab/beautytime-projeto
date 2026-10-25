// Stores recurring weekly service periods for a professional.
table professional_hours {
  auth = false

  schema {
    int id
    int professional_id {
      table = "professional"
    }
    int day_of_week
    int start_minute
    int end_minute
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "professional_id"}, {name: "day_of_week"}]}
  ]
  guid = "BkaIw-IOsTjuGjW1OTJ6XSuqQxg"
}
