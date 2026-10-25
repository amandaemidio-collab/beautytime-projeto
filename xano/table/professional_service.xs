// Stores the many-to-many relationship between professionals and services.
table professional_service {
  auth = false

  schema {
    int id
    int professional_id {
      table = "professional"
    }
    int service_id {
      table = "service"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "professional_id"}]}
    {type: "btree", field: [{name: "service_id"}]}
    {
      type : "btree|unique"
      field: [{name: "professional_id"}, {name: "service_id"}]
    }
  ]
  guid = "dhvtg6IL7d4PCNPoZg6snc_SS_A"
}
