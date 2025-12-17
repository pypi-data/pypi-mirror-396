from datetime import datetime
from typing import List

from peewee import (
    AutoField,
    CharField,
    DateTimeField,
    FloatField, IntegerField,
    Model,
    SqliteDatabase as PeeweeSqliteDatabase,
    ModelSelect,
    ModelDelete,
    chunked,
    fn
)

from xmpy.包_交易核心.模块_常数 import 类_交易所, 类_周期
from xmpy.包_交易核心.模块_对象 import 类_K线数据, 类_行情数据
from xmpy.包_交易核心.模块_工具 import 获取文件路径
from xmpy.包_交易核心.模块_基础数据库 import (
    类_基础数据库,
    类_K线概览,
    数据库时区,
    类_Tick概览,
    转换时区
)

数据库路径: str = str(获取文件路径("database.db"))
数据库: PeeweeSqliteDatabase = PeeweeSqliteDatabase(数据库路径)


class 类_K线数据表(Model):
    """K线数据表映射对象"""

    标识符: AutoField = AutoField()

    代码: str = CharField()
    交易所: str = CharField()
    时间戳: datetime = DateTimeField()
    周期: str = CharField()

    成交量: float = FloatField()
    成交额: float = FloatField()
    持仓量: float = FloatField()
    开盘价: float = FloatField()
    最高价: float = FloatField()
    最低价: float = FloatField()
    收盘价: float = FloatField()

    class Meta:
        database: PeeweeSqliteDatabase = 数据库
        indexes: tuple = ((("代码", "交易所", "周期", "时间戳"), True),)


class 类_Tick数据表(Model):
    """TICK数据表映射对象"""

    标识符: AutoField = AutoField()

    代码: str = CharField()
    交易所: str = CharField()
    时间戳: datetime = DateTimeField()

    名称: str = CharField()
    成交量: float = FloatField()
    成交额: float = FloatField()
    持仓量: float = FloatField()
    最新价: float = FloatField()
    最新量: float = FloatField()
    涨停价: float = FloatField()
    跌停价: float = FloatField()

    开盘价: float = FloatField()
    最高价: float = FloatField()
    最低价: float = FloatField()
    昨收价: float = FloatField()

    买一价: float = FloatField()
    买二价: float = FloatField(null=True)
    买三价: float = FloatField(null=True)
    买四价: float = FloatField(null=True)
    买五价: float = FloatField(null=True)

    卖一价: float = FloatField()
    卖二价: float = FloatField(null=True)
    卖三价: float = FloatField(null=True)
    卖四价: float = FloatField(null=True)
    卖五价: float = FloatField(null=True)

    买一量: float = FloatField()
    买二量: float = FloatField(null=True)
    买三量: float = FloatField(null=True)
    买四量: float = FloatField(null=True)
    买五量: float = FloatField(null=True)

    卖一量: float = FloatField()
    卖二量: float = FloatField(null=True)
    卖三量: float = FloatField(null=True)
    卖四量: float = FloatField(null=True)
    卖五量: float = FloatField(null=True)

    本地时间: datetime = DateTimeField(null=True)

    class Meta:
        database: PeeweeSqliteDatabase = 数据库
        indexes: tuple = ((("代码", "交易所", "时间戳"), True),)


class 类_K线概览表(Model):
    """K线汇总数据表映射对象"""

    标识符: AutoField = AutoField()

    代码: str = CharField()
    交易所: str = CharField()
    周期: str = CharField()
    数量: int = IntegerField()
    起始时间: datetime = DateTimeField()
    结束时间: datetime = DateTimeField()

    class Meta:
        database: PeeweeSqliteDatabase = 数据库
        indexes: tuple = ((("代码", "交易所", "周期"), True),)


class 类_Tick概览表(Model):
    """Tick汇总数据表映射对象"""

    标识符: AutoField = AutoField()

    代码: str = CharField()
    交易所: str = CharField()
    数量: int = IntegerField()
    起始时间: datetime = DateTimeField()
    结束时间: datetime = DateTimeField()

    class Meta:
        database: PeeweeSqliteDatabase = 数据库
        indexes: tuple = ((("代码", "交易所"), True),)

class 类_SQLite数据库(类_基础数据库):
    """SQLite数据库接口"""

    def __init__(self) -> None:
        """"""
        self.数据库: PeeweeSqliteDatabase = 数据库
        self.数据库.connect()
        self.数据库.create_tables([类_K线数据表, 类_Tick数据表, 类_K线概览表, 类_Tick概览表])

    def 保存K线数据(self, K线列表: List[类_K线数据], 流式存储: bool = False) -> bool:
        """保存K线数据"""
        首条K线: 类_K线数据 = K线列表[0]
        代码: str = 首条K线.代码
        交易所: 类_交易所 = 首条K线.交易所
        周期: 类_周期 = 首条K线.周期

        数据列表: list = []
        for 单条K线 in K线列表:
            单条K线.时间戳 = 转换时区(单条K线.时间戳)

            数据字典: dict = 单条K线.__dict__
            数据字典["交易所"] = 数据字典["交易所"].value
            数据字典["周期"] = 数据字典["周期"].value
            数据字典.pop("网关名称")
            数据字典.pop("代码_交易所")
            数据列表.append(数据字典)

        with self.数据库.atomic():
            for 数据块 in chunked(数据列表, 5):
                类_K线数据表.insert_many(数据块).on_conflict_replace().execute()

        概览记录: 类_K线概览表 = 类_K线概览表.get_or_none(
            类_K线概览表.代码 == 代码,
            类_K线概览表.交易所 == 交易所.value,
            类_K线概览表.周期 == 周期.value,
        )

        if not 概览记录:
            概览记录 = 类_K线概览表()
            概览记录.代码 = 代码
            概览记录.交易所 = 交易所.value
            概览记录.周期 = 周期.value
            概览记录.起始时间 = K线列表[0].时间戳
            概览记录.结束时间 = K线列表[-1].时间戳
            概览记录.数量 = len(K线列表)
        elif 流式存储:
            概览记录.结束时间 = K线列表[-1].时间戳
            概览记录.数量 += len(K线列表)
        else:
            概览记录.起始时间 = min(K线列表[0].时间戳, 概览记录.起始时间)
            概览记录.结束时间 = max(K线列表[-1].时间戳, 概览记录.结束时间)

            查询语句: ModelSelect = 类_K线数据表.select().where(
                (类_K线数据表.代码 == 代码)
                & (类_K线数据表.交易所 == 交易所.value)
                & (类_K线数据表.周期 == 周期.value)
            )
            概览记录.数量 = 查询语句.count()
        概览记录.save()
        return True

    def 保存Tick数据(self, Tick列表: List[类_行情数据], 流式存储: bool = False) -> bool:
        """保存TICK数据"""
        首条Tick: 类_行情数据 = Tick列表[0]
        代码: str = 首条Tick.代码
        交易所: 类_交易所 = 首条Tick.交易所

        数据列表: list = []
        for 单条Tick in Tick列表:
            单条Tick.时间戳 = 转换时区(单条Tick.时间戳)

            数据字典: dict = 单条Tick.__dict__
            数据字典["交易所"] = 数据字典["交易所"].value
            数据字典.pop("网关名称")
            数据字典.pop("代码_交易所")
            数据列表.append(数据字典)

        with self.数据库.atomic():
            for 数据块 in chunked(数据列表, 10):
                类_Tick数据表.insert_many(数据块).on_conflict_replace().execute()

        概览记录: 类_Tick概览表 = 类_Tick概览表.get_or_none(
            类_Tick概览表.代码 == 代码,
            类_Tick概览表.交易所 == 交易所.value,
        )

        if not 概览记录:
            概览记录 = 类_Tick概览表()
            概览记录.代码 = 代码
            概览记录.交易所 = 交易所.value
            概览记录.起始时间 = Tick列表[0].时间戳
            概览记录.结束时间 = Tick列表[-1].时间戳
            概览记录.数量 = len(Tick列表)
        elif 流式存储:
            概览记录.结束时间 = Tick列表[-1].时间戳
            概览记录.数量 += len(Tick列表)
        else:
            概览记录.起始时间 = min(Tick列表[0].时间戳, 概览记录.起始时间)
            概览记录.结束时间 = max(Tick列表[-1].时间戳, 概览记录.结束时间)

            查询语句: ModelSelect = 类_Tick数据表.select().where(
                (类_Tick数据表.代码 == 代码)
                & (类_Tick数据表.交易所 == 交易所.value)
            )
            概览记录.数量 = 查询语句.count()

        概览记录.save()
        return True

    def 加载K线数据(
            self,
            代码: str,
            交易所: 类_交易所,
            周期: 类_周期,
            开始时间: datetime,
            结束时间: datetime
    ) -> List[类_K线数据]:
        """读取K线数据"""
        查询语句: ModelSelect = (
            类_K线数据表.select().where(
                (类_K线数据表.代码 == 代码)
                & (类_K线数据表.交易所 == 交易所.value)
                & (类_K线数据表.周期 == 周期.value)
                & (类_K线数据表.时间戳 >= 开始时间)
                & (类_K线数据表.时间戳 <= 结束时间)
            ).order_by(类_K线数据表.时间戳)
        )

        K线列表: List[类_K线数据] = []
        for 数据库K线 in 查询语句:
            K线对象 = 类_K线数据(
                代码=数据库K线.代码,
                交易所=类_交易所(数据库K线.交易所),
                时间戳=datetime.fromtimestamp(数据库K线.时间戳.timestamp(), 数据库时区),
                周期=类_周期(数据库K线.周期),
                成交量=数据库K线.成交量,
                成交额=数据库K线.成交额,
                持仓量=数据库K线.持仓量,
                开盘价=数据库K线.开盘价,
                最高价=数据库K线.最高价,
                最低价=数据库K线.最低价,
                收盘价=数据库K线.收盘价,
                网关名称="数据库"
            )
            K线列表.append(K线对象)
        return K线列表

    def 加载Tick数据(
            self,
            代码: str,
            交易所: 类_交易所,
            开始时间: datetime,
            结束时间: datetime
    ) -> List[类_行情数据]:
        """读取TICK数据"""
        查询语句: ModelSelect = (
            类_Tick数据表.select().where(
                (类_Tick数据表.代码 == 代码)
                & (类_Tick数据表.交易所 == 交易所.value)
                # & (类_Tick数据表.交易所 == 交易所)
                & (类_Tick数据表.时间戳 >= 开始时间)
                & (类_Tick数据表.时间戳 <= 结束时间)
            ).order_by(类_Tick数据表.时间戳)
        )

        Tick列表: List[类_行情数据] = []
        for 数据库Tick in 查询语句:
            Tick对象 = 类_行情数据(
                代码=数据库Tick.代码,
                交易所=类_交易所(数据库Tick.交易所),
                时间戳=datetime.fromtimestamp(数据库Tick.时间戳.timestamp(), 数据库时区),
                名称=数据库Tick.名称,
                成交量=数据库Tick.成交量,
                成交额=数据库Tick.成交额,
                持仓量=数据库Tick.持仓量,
                最新价=数据库Tick.最新价,
                最新量=数据库Tick.最新量,
                涨停价=数据库Tick.涨停价,
                跌停价=数据库Tick.跌停价,
                开盘价=数据库Tick.开盘价,
                最高价=数据库Tick.最高价,
                最低价=数据库Tick.最低价,
                昨收价=数据库Tick.昨收价,
                买一价=数据库Tick.买一价,
                买二价=数据库Tick.买二价,
                买三价=数据库Tick.买三价,
                买四价=数据库Tick.买四价,
                买五价=数据库Tick.买五价,
                卖一价=数据库Tick.卖一价,
                卖二价=数据库Tick.卖二价,
                卖三价=数据库Tick.卖三价,
                卖四价=数据库Tick.卖四价,
                卖五价=数据库Tick.卖五价,
                买一量=数据库Tick.买一量,
                买二量=数据库Tick.买二量,
                买三量=数据库Tick.买三量,
                买四量=数据库Tick.买四量,
                买五量=数据库Tick.买五量,
                卖一量=数据库Tick.卖一量,
                卖二量=数据库Tick.卖二量,
                卖三量=数据库Tick.卖三量,
                卖四量=数据库Tick.卖四量,
                卖五量=数据库Tick.卖五量,
                本地时间=数据库Tick.本地时间,
                网关名称="数据库"
            )
            Tick列表.append(Tick对象)
        return Tick列表

    def 删除K线数据(
            self,
            代码: str,
            交易所: 类_交易所,
            周期: 类_周期,
            开始时间: datetime,
            结束时间: datetime
    ) -> int:
        """删除K线数据"""
        删除操作: ModelDelete = 类_K线数据表.delete().where(
            (类_K线数据表.代码 == 代码)
            & (类_K线数据表.交易所 == 交易所.value)
            & (类_K线数据表.周期 == 周期.value)
            & (类_K线数据表.时间戳 >= 开始时间)
            & (类_K线数据表.时间戳 <= 结束时间)
        )
        删除数量: int = 删除操作.execute()

        概览记录 = 类_K线概览表.get_or_none(
            类_K线概览表.代码 == 代码,
            类_K线概览表.交易所 == 交易所.value,
            类_K线概览表.周期 == 周期.value,
        )

        查询语句: ModelSelect = (
            类_K线数据表.select().where(
                (类_K线数据表.代码 == 代码)
                & (类_K线数据表.交易所 == 交易所.value)
                & (类_K线数据表.周期 == 周期.value)
            ).order_by(类_K线数据表.时间戳)
        )

        K线列表: List[类_K线数据] = []
        for 数据库K线 in 查询语句:
            K线对象 = 类_K线数据(
                代码=数据库K线.代码,
                交易所=类_交易所(数据库K线.交易所),
                时间戳=datetime.fromtimestamp(数据库K线.时间戳.timestamp(), 数据库时区),
                周期=类_周期(数据库K线.周期),
                成交量=数据库K线.成交量,
                成交额=数据库K线.成交额,
                持仓量=数据库K线.持仓量,
                开盘价=数据库K线.开盘价,
                最高价=数据库K线.最高价,
                最低价=数据库K线.最低价,
                收盘价=数据库K线.收盘价,
                网关名称="数据库"
            )
            K线列表.append(K线对象)

        try:

            if not 概览记录:
                概览记录 = 类_K线概览表()
                概览记录.代码 = 代码
                概览记录.交易所 = 交易所.value
                概览记录.周期 = 周期.value
                概览记录.起始时间 = K线列表[0].时间戳.replace(tzinfo=None)
                概览记录.结束时间 = K线列表[-1].时间戳.replace(tzinfo=None)
                概览记录.数量 = len(K线列表)
            else:
                if K线列表[0].时间戳.replace(tzinfo=None) > 概览记录.起始时间:
                    概览记录.起始时间 = K线列表[0].时间戳.replace(tzinfo=None)
                概览记录.起始时间 = min(K线列表[0].时间戳.replace(tzinfo=None), 概览记录.起始时间)
                概览记录.结束时间 = max(K线列表[-1].时间戳.replace(tzinfo=None), 概览记录.结束时间)
                概览记录.数量 = 查询语句.count()

            概览记录.save()
        except IndexError:
            # 如果 Tick列表 为空（没有数据），捕获 IndexError 并提示合约代码错误
            raise ValueError("查询列表为空，请检查'合约代码和交易所'是否输入正确")
        except Exception as e:
            # 其他错误正常抛出
            raise e
        return 删除数量

    def 删除Tick数据(
            self,
            代码: str,
            交易所: 类_交易所,
            开始时间: datetime,
            结束时间: datetime
    ) -> int:
        """删除TICK数据, 注意：和删除K线 <= 不同，tick是 < 结束时间"""
        删除操作: ModelDelete = 类_Tick数据表.delete().where(
            (类_Tick数据表.代码 == 代码)
            & (类_Tick数据表.交易所 == 交易所.value)
            & (类_Tick数据表.时间戳 >= 开始时间)
            & (类_Tick数据表.时间戳 < 结束时间)
        )
        删除数量: int = 删除操作.execute()

        概览记录: 类_Tick概览表 = 类_Tick概览表.get_or_none(
            类_Tick概览表.代码 == 代码,
            类_Tick概览表.交易所 == 交易所.value,
        )

        查询语句: ModelSelect = (
            类_Tick数据表.select().where(
                (类_Tick数据表.代码 == 代码)
                & (类_Tick数据表.交易所 == 交易所.value)
            ).order_by(类_Tick数据表.时间戳)
        )

        Tick列表: List[类_行情数据] = []
        for 数据库Tick in 查询语句:
            Tick对象 = 类_行情数据(
                代码=数据库Tick.代码,
                交易所=类_交易所(数据库Tick.交易所),
                时间戳=datetime.fromtimestamp(数据库Tick.时间戳.timestamp(), 数据库时区),
                名称=数据库Tick.名称,
                成交量=数据库Tick.成交量,
                成交额=数据库Tick.成交额,
                持仓量=数据库Tick.持仓量,
                最新价=数据库Tick.最新价,
                最新量=数据库Tick.最新量,
                涨停价=数据库Tick.涨停价,
                跌停价=数据库Tick.跌停价,
                开盘价=数据库Tick.开盘价,
                最高价=数据库Tick.最高价,
                最低价=数据库Tick.最低价,
                昨收价=数据库Tick.昨收价,
                买一价=数据库Tick.买一价,
                买二价=数据库Tick.买二价,
                买三价=数据库Tick.买三价,
                买四价=数据库Tick.买四价,
                买五价=数据库Tick.买五价,
                卖一价=数据库Tick.卖一价,
                卖二价=数据库Tick.卖二价,
                卖三价=数据库Tick.卖三价,
                卖四价=数据库Tick.卖四价,
                卖五价=数据库Tick.卖五价,
                买一量=数据库Tick.买一量,
                买二量=数据库Tick.买二量,
                买三量=数据库Tick.买三量,
                买四量=数据库Tick.买四量,
                买五量=数据库Tick.买五量,
                卖一量=数据库Tick.卖一量,
                卖二量=数据库Tick.卖二量,
                卖三量=数据库Tick.卖三量,
                卖四量=数据库Tick.卖四量,
                卖五量=数据库Tick.卖五量,
                本地时间=数据库Tick.本地时间,
                网关名称="数据库"
            )
            Tick列表.append(Tick对象)

        try:
            if not 概览记录:
                概览记录 = 类_Tick概览表()
                概览记录.代码 = 代码
                概览记录.交易所 = 交易所.value
                概览记录.起始时间 = Tick列表[0].时间戳.replace(tzinfo=None,microsecond=0)
                概览记录.结束时间 = Tick列表[-1].时间戳.replace(tzinfo=None,microsecond=0)
                概览记录.数量 = len(Tick列表)
            else:
                if Tick列表[0].时间戳.replace(tzinfo=None,microsecond=0) > 概览记录.起始时间:
                    概览记录.起始时间 = Tick列表[0].时间戳.replace(tzinfo=None,microsecond=0)
                概览记录.起始时间 = min(Tick列表[0].时间戳.replace(tzinfo=None,microsecond=0), 概览记录.起始时间)
                概览记录.结束时间 = max(Tick列表[-1].时间戳.replace(tzinfo=None,microsecond=0), 概览记录.结束时间)
                概览记录.数量 = 查询语句.count()

            概览记录.save()
        except IndexError:
            # 如果 Tick列表 为空（没有数据），捕获 IndexError 并提示合约代码错误
            raise ValueError("查询列表为空，请检查'合约代码和交易所'是否输入正确")
        except Exception as e:
            # 其他错误正常抛出
            raise e
        return 删除数量

    def 获取K线概览(self) -> List[类_K线概览]:
        """查询数据库中的K线汇总信息"""
        数据总量: int = 类_K线数据表.select().count()
        概览数量: int = 类_K线概览表.select().count()
        if 数据总量 and not 概览数量:
            self.初始化K线概览()

        查询语句: ModelSelect = 类_K线概览表.select()
        概览列表: List[类_K线概览] = []
        for 概览项 in 查询语句:
            概览项.交易所 = 类_交易所(概览项.交易所)
            概览项.周期 = 类_周期(概览项.周期)
            概览列表.append(概览项)
        return 概览列表

    def 获取Tick概览(self) -> List[类_Tick概览]:
        """查询数据库中的Tick汇总信息"""
        查询语句: ModelSelect = 类_Tick概览表.select()
        概览列表: list = []
        for 概览项 in 查询语句:
            概览项.交易所 = 类_交易所(概览项.交易所)
            概览列表.append(概览项)
        return 概览列表

    def 初始化K线概览(self) -> None:
        """初始化数据库中的K线汇总信息"""
        聚合查询 = (
            类_K线数据表.select(
                类_K线数据表.代码,
                类_K线数据表.交易所,
                类_K线数据表.周期,
                fn.COUNT(类_K线数据表.标识符).alias("数量")
            ).group_by(
                类_K线数据表.代码,
                类_K线数据表.交易所,
                类_K线数据表.周期
            )
        )

        for 数据项 in 聚合查询:
            新概览 = 类_K线概览表()
            新概览.代码 = 数据项.代码
            新概览.交易所 = 数据项.交易所
            新概览.周期 = 数据项.周期
            新概览.数量 = 数据项.数量

            首条K线 = (
                类_K线数据表.select()
                .where(
                    (类_K线数据表.代码 == 数据项.代码)
                    & (类_K线数据表.交易所 == 数据项.交易所)
                    & (类_K线数据表.周期 == 数据项.周期)
                )
                .order_by(类_K线数据表.时间戳.asc())
                .first()
            )
            新概览.起始时间 = 首条K线.时间戳

            末条K线 = (
                类_K线数据表.select()
                .where(
                    (类_K线数据表.代码 == 数据项.代码)
                    & (类_K线数据表.交易所 == 数据项.交易所)
                    & (类_K线数据表.周期 == 数据项.周期)
                )
                .order_by(类_K线数据表.时间戳.desc())
                .first()
            )
            新概览.结束时间 = 末条K线.时间戳

            新概览.save()