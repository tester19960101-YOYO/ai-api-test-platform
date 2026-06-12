from sqlalchemy import BigInteger, Integer

BigIntPrimaryKey = BigInteger().with_variant(Integer, "sqlite")
