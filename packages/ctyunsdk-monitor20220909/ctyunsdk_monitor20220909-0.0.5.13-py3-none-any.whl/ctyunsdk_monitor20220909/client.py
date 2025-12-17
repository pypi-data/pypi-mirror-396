from dataclasses import asdict

from ctyun_openapi_sdk_core import CtyunClient, Credential, ClientConfig, CtyunRequestException

from .models import *


class MonitorClient:
    def __init__(self, client_config: ClientConfig):
        self.client_config = client_config
        self.ctyun_client = CtyunClient()
        self.credential = Credential(self.client_config.access_key_id, self.client_config.access_key_secret)
        self.endpoint = self.client_config.endpoint

    def v4_monitor_update_event_alarm_rule(self, request: V4MonitorUpdateEventAlarmRuleRequest) -> V4MonitorUpdateEventAlarmRuleResponse:
        """修改事件的告警规则配置信息。"""
        url = f"{self.endpoint}/v4/monitor/update-event-alarm-rule"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorUpdateEventAlarmRuleResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_create_event_alarm_rule(self, request: V4MonitorCreateEventAlarmRuleRequest) -> V4MonitorCreateEventAlarmRuleResponse:
        """创建一个事件监控的告警规则。"""
        url = f"{self.endpoint}/v4/monitor/create-event-alarm-rule"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorCreateEventAlarmRuleResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_describe_event_alarm_rule(self, request: V4MonitorDescribeEventAlarmRuleRequest) -> V4MonitorDescribeEventAlarmRuleResponse:
        """查看事件告警规则的详情信息。"""
        url = f"{self.endpoint}/v4/monitor/describe-event-alarm-rule"
        method = 'GET'
        headers = {}
        body = {}
        try:
            params = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorDescribeEventAlarmRuleResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_query_event_alarm_rules(self, request: V4MonitorQueryEventAlarmRulesRequest) -> V4MonitorQueryEventAlarmRulesResponse:
        """根据筛选项查询事件告警规则列表。"""
        url = f"{self.endpoint}/v4/monitor/query-event-alarm-rules"
        method = 'GET'
        headers = {}
        body = {}
        try:
            params = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorQueryEventAlarmRulesResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_events_count_data(self, request: V4MonitorEventsCountDataRequest) -> V4MonitorEventsCountDataResponse:
        """根据指定时间段统计指定事件发生情况。"""
        url = f"{self.endpoint}/v4/monitor/events/count-data"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorEventsCountDataResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_events_query_events(self, request: V4MonitorEventsQueryEventsRequest) -> V4MonitorEventsQueryEventsResponse:
        """获取资源池下指定维度下的事件。"""
        url = f"{self.endpoint}/v4/monitor/events/query-events"
        method = 'GET'
        headers = {}
        body = {}
        try:
            params = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorEventsQueryEventsResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_events_query_list(self, request: V4MonitorEventsQueryListRequest) -> V4MonitorEventsQueryListResponse:
        """根据指定时间段查询事件发生情况。"""
        url = f"{self.endpoint}/v4/monitor/events/query-list"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorEventsQueryListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_events_query_services(self, request: V4MonitorEventsQueryServicesRequest) -> V4MonitorEventsQueryServicesResponse:
        """获取资源池下服务维度信息。"""
        url = f"{self.endpoint}/v4/monitor/events/query-services"
        method = 'GET'
        headers = {}
        body = {}
        try:
            params = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorEventsQueryServicesResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_events_query_detail(self, request: V4MonitorEventsQueryDetailRequest) -> V4MonitorEventsQueryDetailResponse:
        """根据指定时间段查询事件发生情况。"""
        url = f"{self.endpoint}/v4/monitor/events/query-detail"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorEventsQueryDetailResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_delete_alarm_rules(self, request: V4MonitorDeleteAlarmRulesRequest) -> V4MonitorDeleteAlarmRulesResponse:
        """调用此接口可批量删除多个创建告警规则。"""
        url = f"{self.endpoint}/v4/monitor/delete-alarm-rules"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorDeleteAlarmRulesResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_task_center_query_task(self, request: V4MonitorTaskCenterQueryTaskRequest) -> V4MonitorTaskCenterQueryTaskResponse:
        """调用此接口可查询数据导出任务结果。"""
        url = f"{self.endpoint}/v4/monitor/task-center/query-task"
        method = 'GET'
        headers = {}
        body = {}
        try:
            params = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorTaskCenterQueryTaskResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_monitor_board_rename(self, request: V4MonitorMonitorBoardRenameRequest) -> V4MonitorMonitorBoardRenameResponse:
        """重命名监控看板。"""
        url = f"{self.endpoint}/v4/monitor/monitor-board/rename"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorMonitorBoardRenameResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_monitor_board_query_sys_services(self, request: V4MonitorMonitorBoardQuerySysServicesRequest) -> V4MonitorMonitorBoardQuerySysServicesResponse:
        """查询系统看板支持的服务维度。"""
        url = f"{self.endpoint}/v4/monitor/monitor-board/query-sys-services"
        method = 'GET'
        headers = {}
        body = {}
        try:
            params = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorMonitorBoardQuerySysServicesResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_monitor_board_list(self, request: V4MonitorMonitorBoardListRequest) -> V4MonitorMonitorBoardListResponse:
        """查询监控看板列表，仅返回基础信息，不返回视图信息。"""
        url = f"{self.endpoint}/v4/monitor/monitor-board/list"
        method = 'GET'
        headers = {}
        body = {}
        try:
            params = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorMonitorBoardListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_monitor_board_update_sys_resources(self, request: V4MonitorMonitorBoardUpdateSysResourcesRequest) -> V4MonitorMonitorBoardUpdateSysResourcesResponse:
        """为系统看板增加监控资源实例，会用给定的新资源替换原有旧资源。仅支持系统看板。"""
        url = f"{self.endpoint}/v4/monitor/monitor-board/update-sys-resources"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorMonitorBoardUpdateSysResourcesResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_monitor_board_delete(self, request: V4MonitorMonitorBoardDeleteRequest) -> V4MonitorMonitorBoardDeleteResponse:
        """删除监控看板。"""
        url = f"{self.endpoint}/v4/monitor/monitor-board/delete"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorMonitorBoardDeleteResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_monitor_board_copy_view(self, request: V4MonitorMonitorBoardCopyViewRequest) -> V4MonitorMonitorBoardCopyViewResponse:
        """复制已有监控视图。"""
        url = f"{self.endpoint}/v4/monitor/monitor-board/copy-view"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorMonitorBoardCopyViewResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_monitor_board_delete_view(self, request: V4MonitorMonitorBoardDeleteViewRequest) -> V4MonitorMonitorBoardDeleteViewResponse:
        """删除监控视图。"""
        url = f"{self.endpoint}/v4/monitor/monitor-board/delete-view"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorMonitorBoardDeleteViewResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_alarm_rule_query_binding_notice_strategy(self, request: V4MonitorAlarmRuleQueryBindingNoticeStrategyRequest) -> V4MonitorAlarmRuleQueryBindingNoticeStrategyResponse:
        """查询可绑定通知策略的告警规则列表。"""
        url = f"{self.endpoint}/v4/monitor/alarm-rule/query-binding-notice-strategy"
        method = 'GET'
        headers = {}
        body = {}
        try:
            params = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorAlarmRuleQueryBindingNoticeStrategyResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_notice_strategy_describe(self, request: V4MonitorNoticeStrategyDescribeRequest) -> V4MonitorNoticeStrategyDescribeResponse:
        """查看通知策略详情。"""
        url = f"{self.endpoint}/v4/monitor/notice-strategy/describe"
        method = 'GET'
        headers = {}
        body = {}
        try:
            params = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorNoticeStrategyDescribeResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_notice_strategy_unbinding(self, request: V4MonitorNoticeStrategyUnbindingRequest) -> V4MonitorNoticeStrategyUnbindingResponse:
        """通知策略批量解绑告警规则。"""
        url = f"{self.endpoint}/v4/monitor/notice-strategy/unbinding"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorNoticeStrategyUnbindingResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_notice_strategy_binding(self, request: V4MonitorNoticeStrategyBindingRequest) -> V4MonitorNoticeStrategyBindingResponse:
        """通知策略批量绑定告警规则。"""
        url = f"{self.endpoint}/v4/monitor/notice-strategy/binding"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorNoticeStrategyBindingResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_notice_strategy_delete(self, request: V4MonitorNoticeStrategyDeleteRequest) -> V4MonitorNoticeStrategyDeleteResponse:
        """删除通知策略。"""
        url = f"{self.endpoint}/v4/monitor/notice-strategy/delete"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorNoticeStrategyDeleteResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v41_monitor_task_center_query_task(self, request: V41MonitorTaskCenterQueryTaskRequest) -> V41MonitorTaskCenterQueryTaskResponse:
        """调用此接口可查询数据导出任务结果。"""
        url = f"{self.endpoint}/v4.1/monitor/task-center/query-task"
        method = 'GET'
        headers = {}
        body = {}
        try:
            params = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V41MonitorTaskCenterQueryTaskResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_task_center_download(self, request: V4MonitorTaskCenterDownloadRequest) -> V4MonitorTaskCenterDownloadResponse:
        """调用此接口可获取下载链接地址。"""
        url = f"{self.endpoint}/v4/monitor/task-center/download"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorTaskCenterDownloadResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_task_center_delete_task(self, request: V4MonitorTaskCenterDeleteTaskRequest) -> V4MonitorTaskCenterDeleteTaskResponse:
        """参见请求参数说明。"""
        url = f"{self.endpoint}/v4/monitor/task-center/delete-task"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorTaskCenterDeleteTaskResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_task_center_create_task(self, request: V4MonitorTaskCenterCreateTaskRequest) -> V4MonitorTaskCenterCreateTaskResponse:
        """调用此接口可创建数据导出任务。"""
        url = f"{self.endpoint}/v4/monitor/task-center/create-task"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorTaskCenterCreateTaskResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_disable_site_monitor(self, request: V4MonitorDisableSiteMonitorRequest) -> V4MonitorDisableSiteMonitorResponse:
        """调用此接口可禁用站点监控任务。"""
        url = f"{self.endpoint}/v4/monitor/disable-site-monitor"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorDisableSiteMonitorResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_enable_site_monitor(self, request: V4MonitorEnableSiteMonitorRequest) -> V4MonitorEnableSiteMonitorResponse:
        """调用此接口可启用站点监控任务。"""
        url = f"{self.endpoint}/v4/monitor/enable-site-monitor"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorEnableSiteMonitorResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_delete_site_monitor(self, request: V4MonitorDeleteSiteMonitorRequest) -> V4MonitorDeleteSiteMonitorResponse:
        """调用此接口可删除站点监控任务。"""
        url = f"{self.endpoint}/v4/monitor/delete-site-monitor"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorDeleteSiteMonitorResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_create_site_monitor(self, request: V4MonitorCreateSiteMonitorRequest) -> V4MonitorCreateSiteMonitorResponse:
        """调用此接口可创建站点监控任务。"""
        url = f"{self.endpoint}/v4/monitor/create-site-monitor"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorCreateSiteMonitorResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_modify_site_monitor(self, request: V4MonitorModifySiteMonitorRequest) -> V4MonitorModifySiteMonitorResponse:
        """调用此接口可修改站点监控任务。"""
        url = f"{self.endpoint}/v4/monitor/modify-site-monitor"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorModifySiteMonitorResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_query_probe_point(self, request: V4MonitorQueryProbePointRequest) -> V4MonitorQueryProbePointResponse:
        """调用此接口可查询探测节点列表。"""
        url = f"{self.endpoint}/v4/monitor/query-probe-point"
        method = 'GET'
        headers = {}
        body = {}
        try:
            params = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorQueryProbePointResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_describe_probe_point(self, request: V4MonitorDescribeProbePointRequest) -> V4MonitorDescribeProbePointResponse:
        """调用此接口可统计探测点在站点任务下异常详情。"""
        url = f"{self.endpoint}/v4/monitor/describe-probe-point"
        method = 'GET'
        headers = {}
        body = {}
        try:
            params = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorDescribeProbePointResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_hybrid_board_describe_view(self, request: V4MonitorHybridBoardDescribeViewRequest) -> V4MonitorHybridBoardDescribeViewResponse:
        """查看监控大盘视图详细信息。"""
        url = f"{self.endpoint}/v4/monitor/hybrid-board/describe-view"
        method = 'GET'
        headers = {}
        body = {}
        try:
            params = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorHybridBoardDescribeViewResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_hybrid_board_query_view_monitor_data(self, request: V4MonitorHybridBoardQueryViewMonitorDataRequest) -> V4MonitorHybridBoardQueryViewMonitorDataResponse:
        """查询看板下某个视图的数据。"""
        url = f"{self.endpoint}/v4/monitor/hybrid-board/query-view-monitor-data"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorHybridBoardQueryViewMonitorDataResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_hybrid_board_update_view(self, request: V4MonitorHybridBoardUpdateViewRequest) -> V4MonitorHybridBoardUpdateViewResponse:
        """更新已有监控视图。"""
        url = f"{self.endpoint}/v4/monitor/hybrid-board/update-view"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorHybridBoardUpdateViewResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_hybrid_board_copy_view(self, request: V4MonitorHybridBoardCopyViewRequest) -> V4MonitorHybridBoardCopyViewResponse:
        """复制已有监控视图。"""
        url = f"{self.endpoint}/v4/monitor/hybrid-board/copy-view"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorHybridBoardCopyViewResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_hybrid_board_delete_view(self, request: V4MonitorHybridBoardDeleteViewRequest) -> V4MonitorHybridBoardDeleteViewResponse:
        """删除监控视图。"""
        url = f"{self.endpoint}/v4/monitor/hybrid-board/delete-view"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorHybridBoardDeleteViewResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_hybrid_board_create_view(self, request: V4MonitorHybridBoardCreateViewRequest) -> V4MonitorHybridBoardCreateViewResponse:
        """为已存在的监控大盘创建视图。"""
        url = f"{self.endpoint}/v4/monitor/hybrid-board/create-view"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorHybridBoardCreateViewResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_hybrid_board_view_templates(self, request: V4MonitorHybridBoardViewTemplatesRequest) -> V4MonitorHybridBoardViewTemplatesResponse:
        """查询企业云监控大盘模板。"""
        url = f"{self.endpoint}/v4/monitor/hybrid-board/view-templates"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorHybridBoardViewTemplatesResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_hybrid_board_describe_view_template(self, request: V4MonitorHybridBoardDescribeViewTemplateRequest) -> V4MonitorHybridBoardDescribeViewTemplateResponse:
        """查看监控大盘查看模板详情。"""
        url = f"{self.endpoint}/v4/monitor/hybrid-board/describe-view-template"
        method = 'GET'
        headers = {}
        body = {}
        try:
            params = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorHybridBoardDescribeViewTemplateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_hybrid_board_rename(self, request: V4MonitorHybridBoardRenameRequest) -> V4MonitorHybridBoardRenameResponse:
        """监控大盘重命名。"""
        url = f"{self.endpoint}/v4/monitor/hybrid-board/rename"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorHybridBoardRenameResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_hybrid_board_list(self, request: V4MonitorHybridBoardListRequest) -> V4MonitorHybridBoardListResponse:
        """查询监控大盘列表，仅返回基础信息，不返回视图信息。"""
        url = f"{self.endpoint}/v4/monitor/hybrid-board/list"
        method = 'GET'
        headers = {}
        body = {}
        try:
            params = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorHybridBoardListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_hybrid_board_describe(self, request: V4MonitorHybridBoardDescribeRequest) -> V4MonitorHybridBoardDescribeResponse:
        """查看监控大盘详细信息，包括视图信息，不包含监控数据信息。"""
        url = f"{self.endpoint}/v4/monitor/hybrid-board/describe"
        method = 'GET'
        headers = {}
        body = {}
        try:
            params = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorHybridBoardDescribeResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_hybrid_board_delete(self, request: V4MonitorHybridBoardDeleteRequest) -> V4MonitorHybridBoardDeleteResponse:
        """删除监控大盘。"""
        url = f"{self.endpoint}/v4/monitor/hybrid-board/delete"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorHybridBoardDeleteResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_hybrid_board_create(self, request: V4MonitorHybridBoardCreateRequest) -> V4MonitorHybridBoardCreateResponse:
        """创建企业云监控大盘，可以创建空内容，也可以附带视图创建。"""
        url = f"{self.endpoint}/v4/monitor/hybrid-board/create"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorHybridBoardCreateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_intelligent_inspection_disable_inspection_item(self, request: V4MonitorIntelligentInspectionDisableInspectionItemRequest) -> V4MonitorIntelligentInspectionDisableInspectionItemResponse:
        """调用此接口可禁用巡检项。"""
        url = f"{self.endpoint}/v4/monitor/intelligent-inspection/disable-inspection-item"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorIntelligentInspectionDisableInspectionItemResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_intelligent_inspection_query_inspection_item(self, request: V4MonitorIntelligentInspectionQueryInspectionItemRequest) -> V4MonitorIntelligentInspectionQueryInspectionItemResponse:
        """调用此接口可查询巡检项。"""
        url = f"{self.endpoint}/v4/monitor/intelligent-inspection/query-inspection-item"
        method = 'GET'
        headers = {}
        body = {}
        try:
            params = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorIntelligentInspectionQueryInspectionItemResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_intelligent_inspection_enable_inspection_item(self, request: V4MonitorIntelligentInspectionEnableInspectionItemRequest) -> V4MonitorIntelligentInspectionEnableInspectionItemResponse:
        """调用此接口可启用巡检项。"""
        url = f"{self.endpoint}/v4/monitor/intelligent-inspection/enable-inspection-item"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorIntelligentInspectionEnableInspectionItemResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_intelligent_inspection_modify_inspection_item(self, request: V4MonitorIntelligentInspectionModifyInspectionItemRequest) -> V4MonitorIntelligentInspectionModifyInspectionItemResponse:
        """调用此接口可修改巡检项。"""
        url = f"{self.endpoint}/v4/monitor/intelligent-inspection/modify-inspection-item"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorIntelligentInspectionModifyInspectionItemResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_intelligent_inspection_query_history_detail(self, request: V4MonitorIntelligentInspectionQueryHistoryDetailRequest) -> V4MonitorIntelligentInspectionQueryHistoryDetailResponse:
        """调用此接口可查询巡检历史详情。"""
        url = f"{self.endpoint}/v4/monitor/intelligent-inspection/query-history-detail"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorIntelligentInspectionQueryHistoryDetailResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_intelligent_inspection_query_history_list(self, request: V4MonitorIntelligentInspectionQueryHistoryListRequest) -> V4MonitorIntelligentInspectionQueryHistoryListResponse:
        """调用此接口可查询巡检历史列表。"""
        url = f"{self.endpoint}/v4/monitor/intelligent-inspection/query-history-list"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorIntelligentInspectionQueryHistoryListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_intelligent_inspection_query_task_detail(self, request: V4MonitorIntelligentInspectionQueryTaskDetailRequest) -> V4MonitorIntelligentInspectionQueryTaskDetailResponse:
        """调用此接口可查询巡检结果详情。"""
        url = f"{self.endpoint}/v4/monitor/intelligent-inspection/query-task-detail"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorIntelligentInspectionQueryTaskDetailResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_intelligent_inspection_query_task_overview(self, request: V4MonitorIntelligentInspectionQueryTaskOverviewRequest) -> V4MonitorIntelligentInspectionQueryTaskOverviewResponse:
        """调用此接口可查询巡检结果总览。"""
        url = f"{self.endpoint}/v4/monitor/intelligent-inspection/query-task-overview"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorIntelligentInspectionQueryTaskOverviewResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_intelligent_inspection_query_task_anomaly(self, request: V4MonitorIntelligentInspectionQueryTaskAnomalyRequest) -> V4MonitorIntelligentInspectionQueryTaskAnomalyResponse:
        """调用此接口可查询巡检结果异常。"""
        url = f"{self.endpoint}/v4/monitor/intelligent-inspection/query-task-anomaly"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorIntelligentInspectionQueryTaskAnomalyResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_intelligent_inspection_create_task(self, request: V4MonitorIntelligentInspectionCreateTaskRequest) -> V4MonitorIntelligentInspectionCreateTaskResponse:
        """调用此接口可创建巡检任务。"""
        url = f"{self.endpoint}/v4/monitor/intelligent-inspection/create-task"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorIntelligentInspectionCreateTaskResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_intelligent_inspection_onekey_solve(self, request: V4MonitorIntelligentInspectionOnekeySolveRequest) -> V4MonitorIntelligentInspectionOnekeySolveResponse:
        """调用此接口可一键处理巡检任务异常事件。"""
        url = f"{self.endpoint}/v4/monitor/intelligent-inspection/onekey-solve"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorIntelligentInspectionOnekeySolveResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v41_monitor_change_alarm_rules_status(self, request: V41MonitorChangeAlarmRulesStatusRequest) -> V41MonitorChangeAlarmRulesStatusResponse:
        """批量更新告警规则状态为禁用或启用。"""
        url = f"{self.endpoint}/v4.1/monitor/change-alarm-rules-status"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V41MonitorChangeAlarmRulesStatusResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v41_monitor_delete_alarm_rules(self, request: V41MonitorDeleteAlarmRulesRequest) -> V41MonitorDeleteAlarmRulesResponse:
        """调用此接口可批量删除多个告警规则。"""
        url = f"{self.endpoint}/v4.1/monitor/delete-alarm-rules"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V41MonitorDeleteAlarmRulesResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v41_monitor_create_alarm_rule(self, request: V41MonitorCreateAlarmRuleRequest) -> V41MonitorCreateAlarmRuleResponse:
        """创建一个或多个告警规则。"""
        url = f"{self.endpoint}/v4.1/monitor/create-alarm-rule"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V41MonitorCreateAlarmRuleResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v41_monitor_update_alarm_rule(self, request: V41MonitorUpdateAlarmRuleRequest) -> V41MonitorUpdateAlarmRuleResponse:
        """更新指定告警规则， 支持全量字段修改。"""
        url = f"{self.endpoint}/v4.1/monitor/update-alarm-rule"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V41MonitorUpdateAlarmRuleResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v41_monitor_describe_alarm_rule(self, request: V41MonitorDescribeAlarmRuleRequest) -> V41MonitorDescribeAlarmRuleResponse:
        """查看告警规则的详情信息。"""
        url = f"{self.endpoint}/v4.1/monitor/describe-alarm-rule"
        method = 'GET'
        headers = {}
        body = {}
        try:
            params = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V41MonitorDescribeAlarmRuleResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v41_monitor_query_alarm_rules(self, request: V41MonitorQueryAlarmRulesRequest) -> V41MonitorQueryAlarmRulesResponse:
        """根据筛选项查询告警规则列表。"""
        url = f"{self.endpoint}/v4.1/monitor/query-alarm-rules"
        method = 'GET'
        headers = {}
        body = {}
        try:
            params = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V41MonitorQueryAlarmRulesResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_canvas_query_resource_child(self, request: V4MonitorCanvasQueryResourceChildRequest) -> V4MonitorCanvasQueryResourceChildResponse:
        """查询资源子设备信息。"""
        url = f"{self.endpoint}/v4/monitor/canvas/query-resource-child"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorCanvasQueryResourceChildResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_canvas_query_history_data(self, request: V4MonitorCanvasQueryHistoryDataRequest) -> V4MonitorCanvasQueryHistoryDataResponse:
        """查询指定时间段内的画布数据"""
        url = f"{self.endpoint}/v4/monitor/canvas/query-history-data"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorCanvasQueryHistoryDataResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_canvas_query_view_data(self, request: V4MonitorCanvasQueryViewDataRequest) -> V4MonitorCanvasQueryViewDataResponse:
        """查询指定时间段内的画布数据"""
        url = f"{self.endpoint}/v4/monitor/canvas/query-view-data"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorCanvasQueryViewDataResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_canvas_query_resource_list(self, request: V4MonitorCanvasQueryResourceListRequest) -> V4MonitorCanvasQueryResourceListResponse:
        """根据筛选条件查询资源池下指定产品的列表。"""
        url = f"{self.endpoint}/v4/monitor/canvas/query-resource-list"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorCanvasQueryResourceListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_canvas_query_region_deploy(self, request: V4MonitorCanvasQueryRegionDeployRequest) -> V4MonitorCanvasQueryRegionDeployResponse:
        """查询资源池画布"""
        url = f"{self.endpoint}/v4/monitor/canvas/query-region-deploy"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorCanvasQueryRegionDeployResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_canvas_query_resource_detail(self, request: V4MonitorCanvasQueryResourceDetailRequest) -> V4MonitorCanvasQueryResourceDetailResponse:
        """查询资源详情信息。"""
        url = f"{self.endpoint}/v4/monitor/canvas/query-resource-detail"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, V4MonitorCanvasQueryResourceDetailResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def lcm_test003(self, request: LcmTest003Request) -> LcmTest003Response:
        """
        该接口提供用户多台云主机信息查询功能，用户可以根据此接口的返回值得到多台云主机信息。该接口相较于/v4/ecs/list-instances提供更精简的云主机信息，拥有更高的查找效率
        准备工作：
          构造请求：在调用前需要了解如何构造请求，详情查看：[构造请求](https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=%u6784%u9020%u8BF7%u6C42&data=87&vid=81)
          认证鉴权：openapi请求需要进行加密调用，详细查看：[认证鉴权](https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=%u6784%u9020%u8BF7%u6C42&data=87&vid=81)
        注意事项：
          分页查询：当前查询结果以分页形式进行展示，单次查询最多显示50条数据
          匹配查找：可以通过部分字段进行匹配筛选数据，无符合条件的为空，在指定多台云主机ID的情况下，只返回匹配到的云主机信息。推荐每次使用单个条件查找
        """
        url = f"{self.endpoint}/v5/lcmTest003"
        method = 'POST'
        headers = {}
        params = {}
        try:
            body = asdict(request)
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                params=params,
                headers=headers,
                body=body
            )
            return self.ctyun_client.handle_response(response, LcmTest003Response)
        except Exception as e:
            raise CtyunRequestException(str(e))



