from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    create_engine,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
)


# TODO look up how to support unicode in string fields where necessary

Base = declarative_base()


class AssetClass(Base):
    __tablename__ = 'asset_class'
    id = Column(Integer, primary_key=True)  # could use a MySQL TINYINT, or get rid of this table entirely and use an ENUM.
    name = Column(String(255), nullable=False)


class InstrumentType(Base):
    __tablename__ = 'instrument_type'
    id = Column(Integer, primary_key=True)  # could use MySQL TINYINT, or eliminate id and use ENUM for name
    name = Column(String(255), nullable=False)

    # It wasn't stated explicitly, but I assume that all instruments of a
    # given instrument type have the same asset class.
    asset_class = Column(Integer, ForeignKey(AssetClass.id))


class Company(Base):
    __tablename__ = 'company'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(10000), nullable=False)


class Instrument(Base):
    __tablename__ = 'instrument'
    id = Column(Integer, primary_key=True)
    type = Column(Integer, ForeignKey(InstrumentType.id), nullable=False)
    isin = Column(String(12), nullable=False)  # use MySQL CHAR for fixed-length string
    name = Column(String(255), nullable=False)  # check if 255 is long enough

    # Spec says "Companies [...] can have multiple instruments." I'm
    # not sure what it means for a company to "have" an instrument. If
    # a company "has" a mutual fund, does that mean that it manages
    # the fund, owns shares in the fund, or has issued stock that is
    # held by the fund?  Can multiple companies "have" the same
    # instrument or not? I'm assuming not. If that assumption is
    # invalid, make a separate table for the company-instrument
    # association.
    company = Column(Integer, ForeignKey(Company.id), nullable=True)


class ClientPortfolio(Base):
    __tablename__ = 'client_portfolio'
    id = Column(Integer, primary_key=True)
    # The spec doesn't mention any other fields, but I assume
    # there would be things like a name and a reference to a client.


class PortfolioHolding(Base):
    __tablename__ = 'portfolio_holding'
    client_portfolio = Column(Integer, ForeignKey(ClientPortfolio.id), primary_key=True)
    instrument = Column(Integer, ForeignKey(Instrument.id), primary_key=True)
    weight = Column(Float, nullable=False)
    # Application must maintain the invariant that the sum of weights
    # across a portfolio is 1. I took the assignment literally here,
    # but wouldn't it be easier to store a valuation and derive the
    # weights at query time, so we don't have to worry about
    # maintaining the sum at 100%? Perhaps not, if the weight is a
    # target rather than a current reality.


class InstrumentComponent(Base):
    __tablename__ = 'instrument_component'
    component_instrument = Column(Integer, ForeignKey(Instrument.id), primary_key=True)
    compound_instrument = Column(Integer, ForeignKey(Instrument.id), primary_key=True)  # TODO find better names, these two are too similar
    weight = Column(Float, nullable=False)  # see comment on PortfolioHolding.weight


class CompanyESG(Base):
    __tablename__ = 'company_esg'
    company = Column(Integer, ForeignKey(Company.id), primary_key=True)
    date = Column(Date, primary_key=True)

    # Assuming all three must be present. If missing values are allowed, split this into three tables.
    e = Column(Float, nullable=False)
    s = Column(Float, nullable=False)
    g = Column(Float, nullable=False)
    # Combined score can be derived from e, s, and g, so it is not
    # stored.
    #
    # We might need to materialize the derived scores for fast
    # querying, e.g. to find the n highest-scoring companies in a
    # large set. If that becomes necessary, do in a separate table
    # rather than adding a field here, to keep a clear separation
    # between normalized data and materialized derived data. I want to
    # be able to drop the score table and recreate it from scratch if
    # necessary.


# Commenting this out because a Client Portfolio's ESG scores can be
# derived from those of the instruments it contains, which are stored
# in this database. If for efficiency reasons we need to pre-compute
# these scores, I would uncomment this but give it a name that makes
# it clear that it's a denormalization, e.g. derived_client_portfolio_esg.
# class ClientPortfolioESG(Base):
#     __tablename__ = 'client_portfolio_esg'
#     client_portfolio = Column(Integer, ForeignKey(ClientPortfolio.id), primary_key=True)
#     date = Column(Date, primary_key=True)
#     e = Column(Float, nullable=False)
#     s = Column(Float, nullable=False)
#     g = Column(Float, nullable=False)


# If we're using a normalized representation, only atomic
# (non-compound) instruments should have ESG scores stored in this
# table. The current schema doesn't enforce that. To enforce it at the
# DB level we could make separate tables for atomic instruments and
# compound instruments, but that might make some queries slower and/or
# more cumbersome
class InstrumentESG(Base):
    __tablename__ = 'instrument_esg'
    instrument = Column(Integer, ForeignKey(Instrument.id), primary_key=True)
    date = Column(Date, primary_key=True)
    e = Column(Float, nullable=False)
    s = Column(Float, nullable=False)
    g = Column(Float, nullable=False)

# There's redundancy among the different ESG classes. If that leads to
# a lot of redundancy in application code, might want to replace them
# all with a single class whose composite primary key has a third
# component which indicates whether the entity is a Company,
# ClientPortfolio, or Instrument. Then you lose the ability to enforce
# the foreign key constraint at the db level, but I think the ORM can
# enforce it.


def dump(sql, *multiparams, **params):
    print sql.compile(dialect=engine.dialect)

engine = create_engine('mysql://', strategy='mock', executor=dump)


Base.metadata.create_all(engine, checkfirst=False)
