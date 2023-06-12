import time, json
from datetime import datetime
import uuid

def get_uuid(v):
    uuid_ = uuid.uuid5(name=str(v), namespace=uuid.NAMESPACE_OID)
    return uuid_

class DdsMessageProcessor:
    def __init__(self,KafkaConsumer,KafkaProducer,DdsRepository,_batch_size,logger) -> None:
        self._consumer = KafkaConsumer
        self._producer = KafkaProducer
        self._dds_repository = DdsRepository
        if _batch_size:
            self._batch_size = _batch_size
        else:
            self._batch_size = 100
        self._logger = logger
    


        # Витрина №1
    def cdm_user_category_counters(self,msg):
        payload = msg['payload']

        user_uuid = str(get_uuid(payload['user']['id']))
        for product in payload['products']:
            out = {}
            category_uuid = str(get_uuid(product['category']))

            out['mart'] = 'user_category_counters'
            out['user_id'] = user_uuid
            out['category_id'] = category_uuid
            out['category_name'] = product['category']
            out['order_cnt'] = product['quantity']

            self._producer.produce(out)

    # Витрина №2
    def cdm_user_product_counters(self,msg):
        payload = msg['payload']

        user_uuid = str(get_uuid(payload['user']['id']))
        for product in payload['products']:
            out = {}
            product_uuid = str(get_uuid(product['id']))

            out['mart'] = 'user_product_counters'
            out['user_id'] = user_uuid
            out['product_id'] = product_uuid
            out['product_name'] = product['name']
            out['order_cnt'] = product['quantity']
            
            self._producer.produce(out)



    # Хаб с категориями
    def put_category_hub(self,msg):
        categories = []
        payload = msg['payload']
        for product in payload['products']:
            categories.append(product['category'])
        for category in categories:
            columns = ['category_name', 'load_src']
            values = [category,'stg-service-orders']
            self._dds_repository.insert_hub('category',columns,values)

    # Хаб с заказами
    def put_order_hub(self,msg):
        if msg['object_type'] == 'order':
            payload = msg['payload']

            order_id = payload['id']
            order_dt = payload['date']
            columns = ['order_id','order_dt','load_src']

            values = [order_id,order_dt,'stg-service-orders']

            self._dds_repository.insert_hub('order',columns,values)
        else:
            pass

    # Хаб с продуктами
    def put_product_hub(self,msg):
        payload = msg['payload']
        products = []
        for product in payload['products']:
            products.append(product['id'])
        for product_id in products:
            columns = ['product_id', 'load_src']
            values = [product_id,'stg-service-orders']
            self._dds_repository.insert_hub('product',columns,values)

    # Хаб с ресторанами
    def put_restaurant_hub(self,msg):
        restaurant_id = msg['payload']['restaurant']['id']
        columns = ['restaurant_id', 'load_src']
        values = [restaurant_id,'stg-service-orders']
        self._dds_repository.insert_hub('restaurant',columns,values)

    # Хаб с пользователями
    def put_user_hub(self,msg):
        user_id = msg['payload']['user']['id']
        columns = ['user_id', 'load_src']
        values = [user_id,'stg-service-orders']
        self._dds_repository.insert_hub('user',columns,values)

    # Линк order_product
    def put_order_product_link(self,msg):
        payload = msg['payload']
        order_id = payload['id']
        products = []
        for product in payload['products']:
            products.append(product['id'])
        for product_id in products:
            self._dds_repository.insert_link('order',
                        order_id,
                        'product',
                        product_id,
                    'stg-service-orders',
                    )

    # Линк order_user
    def put_order_user_link(self,msg):
        payload = msg['payload']
        order_id = payload['id']
        user_id = payload['user']['id']
        self._dds_repository.insert_link('order',
                        order_id,
                        'user',
                        user_id,
                    'stg-service-orders',
                    )
            
    # Линк product_category
    def put_product_category_link(self,msg):
        payload = msg['payload']
        for product in payload['products']:
            self._dds_repository.insert_link('product',
                        product['id'],
                        'category',
                        product['category'],
                    'stg-service-orders',
                    )
            
    # Линк product_restaurant
    def put_product_restaurant_link(self,msg):
        payload = msg['payload']
        restaurant_id = payload['restaurant']['id']
        products = []
        for product in payload['products']:
            products.append(product['id'])
        for product_id in products:
            self._dds_repository.insert_link('product',
                        product_id,
                        'restaurant',
                        restaurant_id,
                    'stg-service-orders',
                    )

    # Сателлит order_cost
    def put_order_cost_satellit(self,msg):
        hub_name = 'order'
        satellit_name = 'cost'
        payload = msg['payload']
        order_id = payload['id']
        order_cost = payload['cost']
        order_payment = payload['payment']
        columns = [f'h_{hub_name}_pk','cost','payment','load_src']
        values = [order_id,order_cost,order_payment,'stg-']
        self._dds_repository.insert_satellit(hub_name,
                        satellit_name,
                        columns,
                        values,
                        )
        
    # Сателлит order_status
    def put_order_status_satellit(self,msg):
        hub_name = 'order'
        satellit_name = 'status'
        payload = msg['payload']
        order_id = payload['id']
        order_status = payload['status']
        columns = [f'h_{hub_name}_pk','status','load_src']
        values = [order_id,order_status,'stg-']
        self._dds_repository.insert_satellit(hub_name,
                        satellit_name,
                        columns,
                        values,
                        )
        
    # Сателлит product_names
    def put_product_name_satellit(self,msg):
        hub_name = 'product'
        satellit_name = 'names'
        payload = msg['payload']
        for product in payload['products']:
            product_id = product['id']
            product_name = product['name']
            columns = [f'h_{hub_name}_pk','name','load_src']
            values = [product_id,product_name,'stg-']
        self._dds_repository.insert_satellit(hub_name,
                        satellit_name,
                        columns,
                        values,
                        )
        
    # Сателлит restaurant_names
    def put_restaurant_name_satellit(self,msg):
        hub_name = 'restaurant'
        satellit_name = 'names'
        payload = msg['payload']
        restaurant_id = payload['restaurant']['id']
        restaurant_name = payload['restaurant']['name']
        columns = [f'h_{hub_name}_pk','name','load_src']
        values = [restaurant_id,restaurant_name,'stg-']
        self._dds_repository.insert_satellit(hub_name,
                        satellit_name,
                        columns,
                        values,
                        )
        
    # Сателлит user_names
    def put_user_names_satellit(self,msg):
        hub_name = 'user'
        satellit_name = 'names'
        payload = msg['payload']
        user_id = payload['user']['id']
        username = payload['user']['name']
        userlogin = payload['user']['name']
        columns = [f'h_{hub_name}_pk','username','userlogin','load_src']
        values = [user_id,username,userlogin,'stg-']
        self._dds_repository.insert_satellit(hub_name,
                        satellit_name,
                        columns,
                        values,
                        )

    # функция, которая будет вызываться по расписанию.
    def run(self) -> None:
        # Пишем в лог, что джоб был запущен.
        self._logger.info(f"START START STARTSTARTSTARTSTART STARTм м START{datetime.utcnow()}: START")

        i = 0
        while i < self._batch_size:
            message = self._consumer.consume()
            self._logger.info(i)
            i = i+1
            if message is None:
                break
            if message.get('object_id'):

                try:
                    self.cdm_user_category_counters(message)
                    self.cdm_user_product_counters(message)

                    # Hubs
                    self.put_category_hub(message)
                    self.put_order_hub(message)
                    self.put_product_hub(message)
                    self.put_restaurant_hub(message)
                    self.put_user_hub(message)

                    # Satellits
                    self.put_order_cost_satellit(message)
                    self.put_order_status_satellit(message)
                    self.put_product_name_satellit(message)
                    self.put_restaurant_name_satellit(message)
                    self.put_user_names_satellit(message)

                    # Links
                    self.put_order_product_link(message)
                    self.put_order_user_link(message)
                    self.put_product_category_link(message)
                    self.put_product_restaurant_link(message)
                except:
                    pass
                

        # Пишем в лог, что джоб успешно завершен.
        self._logger.info(message)
        self._logger.info(f"{datetime.utcnow()}: FINISH")