table MOCK_DATA {
  auth = false

  schema {
    int id
    text first_name?
    text last_name?
    email email?
    text gender?
    text ip_address?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "gin", field: [{name: "xdo", op: "jsonb_path_op"}]}
  ]

  guid = "P9bGsy9_R7c7WIcoZIj6PGlc870"
}