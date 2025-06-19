import strawberry
from wasmer_app.schema.mutation import Mutation
from wasmer_app.schema.query import Query

schema = strawberry.Schema(query=Query, mutation=Mutation)
