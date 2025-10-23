ADSWeb API endpoints (base URL: http://127.0.0.1:8002/adsweb/api/v1)

Patients
- GET  /patients                      -> List patients
- GET  /patients/{patient_id}         -> Get patient by ID
- POST /patients                      -> Create patient (requires admin/staff role)
- PUT  /patient/{patient_id}          -> Update patient (requires admin/staff)
- DELETE /patient/{patient_id}        -> Delete patient (requires admin)
- GET  /patient/search/{search_string} -> Search patients

Addresses
- GET  /addresses                     -> List addresses
- POST /addresses                     -> Create address (requires admin/staff)

Example curl to create an address (replace <TOKEN>):

```bash
curl -X POST "http://127.0.0.1:8002/adsweb/api/v1/addresses" \
	-H "Authorization: Bearer <TOKEN>" \
	-H "Content-Type: application/json" \
	-d '{
		"street":"456 Side St",
		"city":"Newcity",
		"state":"TX",
		"postal_code":"99999",
		"country":"USA"
	}'
```

Auth
- POST /auth/register                 -> Register new user (query params: username,email,password)
- POST /auth/token                    -> Obtain OAuth2 token (form fields: username, password)

Other notes
- API prefix: /adsweb/api/v1
- Use Authorization: Bearer <token> header for protected endpoints
- Create address first and use its `id` as `address_id` when creating patients

Promote a user to admin (local)
--------------------------------
Run the included helper script to promote a user to the `admin` role. Replace the username as needed:

```
export PYTHONPATH=/Final-project
python3 /Final-project/scripts/promote_admin.py Asmaa
```
