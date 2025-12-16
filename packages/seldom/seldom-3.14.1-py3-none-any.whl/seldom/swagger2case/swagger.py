import seldom


class TestRequest(seldom.TestCase): 
    
    def test_pet_petId_uploadImage_api_post(self):
        url = f"https://petstore.swagger.io/pet/{petId}/uploadImage"
        params = {}
        headers = {}
        headers["Content-Type"] = "multipart/form-data"
        data = {"additionalMetadata": additionalMetadata, "file": file}
        r = self.post(url, headers=headers, params=params, data=data)
        print(r.status_code)


    def test_pet_api_post(self):
        url = f"https://petstore.swagger.io/pet"
        params = {}
        headers = {}
        headers["Content-Type"] = "application/json"
        data = {}
        r = self.post(url, headers=headers, params=params, data=data)
        print(r.status_code)


    def test_pet_api_put(self):
        url = f"https://petstore.swagger.io/pet"
        params = {}
        headers = {}
        headers["Content-Type"] = "application/json"
        data = {}
        r = self.put(url, headers=headers, params=params, data=data)
        print(r.status_code)


    def test_pet_findByStatus_api_get(self):
        url = f"https://petstore.swagger.io/pet/findByStatus"
        params = {"status": status}
        headers = {}
        headers["Content-Type"] = "application/json"
        data = {}
        r = self.get(url, headers=headers, params=params, data=data)
        print(r.status_code)


    def test_pet_findByTags_api_get(self):
        url = f"https://petstore.swagger.io/pet/findByTags"
        params = {"tags": tags}
        headers = {}
        headers["Content-Type"] = "application/json"
        data = {}
        r = self.get(url, headers=headers, params=params, data=data)
        print(r.status_code)


    def test_pet_petId_api_get(self):
        url = f"https://petstore.swagger.io/pet/{petId}"
        params = {}
        headers = {}
        headers["Content-Type"] = "application/json"
        data = {}
        r = self.get(url, headers=headers, params=params, data=data)
        print(r.status_code)


    def test_pet_petId_api_post(self):
        url = f"https://petstore.swagger.io/pet/{petId}"
        params = {}
        headers = {}
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        data = {"name": name, "status": status}
        r = self.post(url, headers=headers, params=params, data=data)
        print(r.status_code)


    def test_pet_petId_api_delete(self):
        url = f"https://petstore.swagger.io/pet/{petId}"
        params = {}
        headers = {"api_key": api_key}
        headers["Content-Type"] = "application/json"
        data = {}
        r = self.delete(url, headers=headers, params=params, data=data)
        print(r.status_code)


    def test_store_order_api_post(self):
        url = f"https://petstore.swagger.io/store/order"
        params = {}
        headers = {}
        headers["Content-Type"] = "application/json"
        data = {}
        r = self.post(url, headers=headers, params=params, data=data)
        print(r.status_code)


    def test_store_order_orderId_api_get(self):
        url = f"https://petstore.swagger.io/store/order/{orderId}"
        params = {}
        headers = {}
        headers["Content-Type"] = "application/json"
        data = {}
        r = self.get(url, headers=headers, params=params, data=data)
        print(r.status_code)


    def test_store_order_orderId_api_delete(self):
        url = f"https://petstore.swagger.io/store/order/{orderId}"
        params = {}
        headers = {}
        headers["Content-Type"] = "application/json"
        data = {}
        r = self.delete(url, headers=headers, params=params, data=data)
        print(r.status_code)


    def test_store_inventory_api_get(self):
        url = f"https://petstore.swagger.io/store/inventory"
        params = {}
        headers = {}
        headers["Content-Type"] = "application/json"
        data = {}
        r = self.get(url, headers=headers, params=params, data=data)
        print(r.status_code)


    def test_user_createWithArray_api_post(self):
        url = f"https://petstore.swagger.io/user/createWithArray"
        params = {}
        headers = {}
        headers["Content-Type"] = "application/json"
        data = {}
        r = self.post(url, headers=headers, params=params, data=data)
        print(r.status_code)


    def test_user_createWithList_api_post(self):
        url = f"https://petstore.swagger.io/user/createWithList"
        params = {}
        headers = {}
        headers["Content-Type"] = "application/json"
        data = {}
        r = self.post(url, headers=headers, params=params, data=data)
        print(r.status_code)


    def test_user_username_api_get(self):
        url = f"https://petstore.swagger.io/user/{username}"
        params = {}
        headers = {}
        headers["Content-Type"] = "application/json"
        data = {}
        r = self.get(url, headers=headers, params=params, data=data)
        print(r.status_code)


    def test_user_username_api_put(self):
        url = f"https://petstore.swagger.io/user/{username}"
        params = {}
        headers = {}
        headers["Content-Type"] = "application/json"
        data = {}
        r = self.put(url, headers=headers, params=params, data=data)
        print(r.status_code)


    def test_user_username_api_delete(self):
        url = f"https://petstore.swagger.io/user/{username}"
        params = {}
        headers = {}
        headers["Content-Type"] = "application/json"
        data = {}
        r = self.delete(url, headers=headers, params=params, data=data)
        print(r.status_code)


    def test_user_login_api_get(self):
        url = f"https://petstore.swagger.io/user/login"
        params = {"username": username, "password": password}
        headers = {}
        headers["Content-Type"] = "application/json"
        data = {}
        r = self.get(url, headers=headers, params=params, data=data)
        print(r.status_code)


    def test_user_logout_api_get(self):
        url = f"https://petstore.swagger.io/user/logout"
        params = {}
        headers = {}
        headers["Content-Type"] = "application/json"
        data = {}
        r = self.get(url, headers=headers, params=params, data=data)
        print(r.status_code)


    def test_user_api_post(self):
        url = f"https://petstore.swagger.io/user"
        params = {}
        headers = {}
        headers["Content-Type"] = "application/json"
        data = {}
        r = self.post(url, headers=headers, params=params, data=data)
        print(r.status_code)


if __name__ == '__main__':
    seldom.main()
    