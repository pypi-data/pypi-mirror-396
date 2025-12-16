# foxy_entities

## Library for managing social media entities

The main goal is to create a social media entity management system for shared storage and load balancing

### Basic usage

#### Inherit the base abc of the entity

~~~python

from foxy_entities import SocialMediaEntity


class FakeSocialMediaEntity(SocialMediaEntity):
    fake_str: str


~~~

#### Add a new entity to the virtual storage

~~~python

entity_controller = EntityController()  
  
entity_controller.add_entity(FakeSocialMediaEntity(fake_str="hello world"))

~~~

#### Get an entity from virtual storage

~~~python

entity = entity_controller.get_entity(FakeSocialMediaEntity)

~~~
	
