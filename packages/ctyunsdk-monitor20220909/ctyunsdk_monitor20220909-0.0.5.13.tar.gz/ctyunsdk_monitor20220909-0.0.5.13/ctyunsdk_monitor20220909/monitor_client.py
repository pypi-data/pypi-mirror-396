from ctyun_python_sdk_core import CtyunClient, Credential, ClientConfig, CtyunRequestException

from .models import *


class MonitorClient:
    def __init__(self, client_config: ClientConfig):
        self.endpoint = client_config.endpoint
        self.credential = Credential(client_config.access_key_id, client_config.access_key_secret)
        self.ctyun_client = CtyunClient(client_config.verify_tls)

    def v4_monitor_update_event_alarm_rule(self, request: V4MonitorUpdateEventAlarmRuleRequest) -> V4MonitorUpdateEventAlarmRuleResponse:
        """修改事件的告警规则配置信息。"""
        url = f"{self.endpoint}/v4/monitor/update-event-alarm-rule"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorDescribeEventAlarmRuleResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_query_event_alarm_rules(self, request: V4MonitorQueryEventAlarmRulesRequest) -> V4MonitorQueryEventAlarmRulesResponse:
        """根据筛选项查询事件告警规则列表。"""
        url = f"{self.endpoint}/v4/monitor/query-event-alarm-rules"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorQueryEventAlarmRulesResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_events_count_data(self, request: V4MonitorEventsCountDataRequest) -> V4MonitorEventsCountDataResponse:
        """根据指定时间段统计指定事件发生情况。"""
        url = f"{self.endpoint}/v4/monitor/events/count-data"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorEventsQueryEventsResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_events_query_list(self, request: V4MonitorEventsQueryListRequest) -> V4MonitorEventsQueryListResponse:
        """根据指定时间段查询事件发生情况。"""
        url = f"{self.endpoint}/v4/monitor/events/query-list"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorEventsQueryServicesResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_events_query_detail(self, request: V4MonitorEventsQueryDetailRequest) -> V4MonitorEventsQueryDetailResponse:
        """根据指定时间段查询事件发生情况。"""
        url = f"{self.endpoint}/v4/monitor/events/query-detail"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorTaskCenterQueryTaskResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_monitor_board_rename(self, request: V4MonitorMonitorBoardRenameRequest) -> V4MonitorMonitorBoardRenameResponse:
        """重命名监控看板。"""
        url = f"{self.endpoint}/v4/monitor/monitor-board/rename"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorMonitorBoardQuerySysServicesResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_monitor_board_list(self, request: V4MonitorMonitorBoardListRequest) -> V4MonitorMonitorBoardListResponse:
        """查询监控看板列表，仅返回基础信息，不返回视图信息。"""
        url = f"{self.endpoint}/v4/monitor/monitor-board/list"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorMonitorBoardListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_monitor_board_update_sys_resources(self, request: V4MonitorMonitorBoardUpdateSysResourcesRequest) -> V4MonitorMonitorBoardUpdateSysResourcesResponse:
        """为系统看板增加监控资源实例，会用给定的新资源替换原有旧资源。仅支持系统看板。"""
        url = f"{self.endpoint}/v4/monitor/monitor-board/update-sys-resources"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorAlarmRuleQueryBindingNoticeStrategyResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_notice_strategy_describe(self, request: V4MonitorNoticeStrategyDescribeRequest) -> V4MonitorNoticeStrategyDescribeResponse:
        """查看通知策略详情。"""
        url = f"{self.endpoint}/v4/monitor/notice-strategy/describe"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorNoticeStrategyDescribeResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_notice_strategy_unbinding(self, request: V4MonitorNoticeStrategyUnbindingRequest) -> V4MonitorNoticeStrategyUnbindingResponse:
        """通知策略批量解绑告警规则。"""
        url = f"{self.endpoint}/v4/monitor/notice-strategy/unbinding"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V41MonitorTaskCenterQueryTaskResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_task_center_download(self, request: V4MonitorTaskCenterDownloadRequest) -> V4MonitorTaskCenterDownloadResponse:
        """调用此接口可获取下载链接地址。"""
        url = f"{self.endpoint}/v4/monitor/task-center/download"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorQueryProbePointResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_describe_probe_point(self, request: V4MonitorDescribeProbePointRequest) -> V4MonitorDescribeProbePointResponse:
        """调用此接口可统计探测点在站点任务下异常详情。"""
        url = f"{self.endpoint}/v4/monitor/describe-probe-point"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorDescribeProbePointResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_hybrid_board_describe_view(self, request: V4MonitorHybridBoardDescribeViewRequest) -> V4MonitorHybridBoardDescribeViewResponse:
        """查看监控大盘视图详细信息。"""
        url = f"{self.endpoint}/v4/monitor/hybrid-board/describe-view"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorHybridBoardDescribeViewResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_hybrid_board_query_view_monitor_data(self, request: V4MonitorHybridBoardQueryViewMonitorDataRequest) -> V4MonitorHybridBoardQueryViewMonitorDataResponse:
        """查询看板下某个视图的数据。"""
        url = f"{self.endpoint}/v4/monitor/hybrid-board/query-view-monitor-data"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorHybridBoardDescribeViewTemplateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_hybrid_board_rename(self, request: V4MonitorHybridBoardRenameRequest) -> V4MonitorHybridBoardRenameResponse:
        """监控大盘重命名。"""
        url = f"{self.endpoint}/v4/monitor/hybrid-board/rename"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorHybridBoardListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_hybrid_board_describe(self, request: V4MonitorHybridBoardDescribeRequest) -> V4MonitorHybridBoardDescribeResponse:
        """查看监控大盘详细信息，包括视图信息，不包含监控数据信息。"""
        url = f"{self.endpoint}/v4/monitor/hybrid-board/describe"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorHybridBoardDescribeResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_hybrid_board_delete(self, request: V4MonitorHybridBoardDeleteRequest) -> V4MonitorHybridBoardDeleteResponse:
        """删除监控大盘。"""
        url = f"{self.endpoint}/v4/monitor/hybrid-board/delete"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorIntelligentInspectionQueryInspectionItemResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_intelligent_inspection_enable_inspection_item(self, request: V4MonitorIntelligentInspectionEnableInspectionItemRequest) -> V4MonitorIntelligentInspectionEnableInspectionItemResponse:
        """调用此接口可启用巡检项。"""
        url = f"{self.endpoint}/v4/monitor/intelligent-inspection/enable-inspection-item"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V41MonitorDescribeAlarmRuleResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v41_monitor_query_alarm_rules(self, request: V41MonitorQueryAlarmRulesRequest) -> V41MonitorQueryAlarmRulesResponse:
        """根据筛选项查询告警规则列表。"""
        url = f"{self.endpoint}/v4.1/monitor/query-alarm-rules"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V41MonitorQueryAlarmRulesResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_canvas_query_resource_child(self, request: V4MonitorCanvasQueryResourceChildRequest) -> V4MonitorCanvasQueryResourceChildResponse:
        """查询资源子设备信息。"""
        url = f"{self.endpoint}/v4/monitor/canvas/query-resource-child"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
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
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorCanvasQueryRegionDeployResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_query_custom_events(self, request: V4MonitorQueryCustomEventsRequest) -> V4MonitorQueryCustomEventsResponse:
        """调用此接口可查询自定义事件。（已废弃）"""
        url = f"{self.endpoint}/v4/monitor/query-custom-events"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorQueryCustomEventsResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_overview_active_alarm(self, request: V4MonitorOverviewActiveAlarmRequest) -> V4MonitorOverviewActiveAlarmResponse:
        """调用此接口可查询当前用户活跃告警数量。"""
        url = f"{self.endpoint}/v4/monitor/overview/active-alarm"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorOverviewActiveAlarmResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_query_alert_history(self, request: V4MonitorQueryAlertHistoryRequest) -> V4MonitorQueryAlertHistoryResponse:
        """查询告警历史, 返回结果按告警历史的触发时间(createTime)降序排列。"""
        url = f"{self.endpoint}/v4/monitor/query-alert-history"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorQueryAlertHistoryResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_query_message_records(self, request: V4MonitorQueryMessageRecordsRequest) -> V4MonitorQueryMessageRecordsResponse:
        """查询通知记录列表。"""
        url = f"{self.endpoint}/v4/monitor/query-message-records"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorQueryMessageRecordsResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_quota(self, request: V4MonitorQuotaRequest) -> V4MonitorQuotaResponse:
        """调用此接口可查询用户资源池指定配额量。"""
        url = f"{self.endpoint}/v4/monitor/quota"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorQuotaResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_unit_query_units(self, request: V4MonitorUnitQueryUnitsRequest) -> V4MonitorUnitQueryUnitsResponse:
        """调用此接口可获取单位组和单位信息。"""
        url = f"{self.endpoint}/v4/monitor/unit/query-units"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorUnitQueryUnitsResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_public_network_probing_query_table_data(self, request: V4MonitorPublicNetworkProbingQueryTableDataRequest) -> V4MonitorPublicNetworkProbingQueryTableDataResponse:
        """查询指定时间段内的表格数据。"""
        url = f"{self.endpoint}/v4/monitor/public-network-probing/query-table-data"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorPublicNetworkProbingQueryTableDataResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_public_network_probing_query_map_data(self, request: V4MonitorPublicNetworkProbingQueryMapDataRequest) -> V4MonitorPublicNetworkProbingQueryMapDataResponse:
        """查询指定时间段内的地图数据。"""
        url = f"{self.endpoint}/v4/monitor/public-network-probing/query-map-data"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorPublicNetworkProbingQueryMapDataResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_monitor_board_export_view_data(self, request: V4MonitorMonitorBoardExportViewDataRequest) -> V4MonitorMonitorBoardExportViewDataResponse:
        """导出看板下某个视图的数据。"""
        url = f"{self.endpoint}/v4/monitor/monitor-board/export-view-data"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorMonitorBoardExportViewDataResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_monitor_board_delete_sys_resources(self, request: V4MonitorMonitorBoardDeleteSysResourcesRequest) -> V4MonitorMonitorBoardDeleteSysResourcesResponse:
        """为系统看板删除监控资源实例。仅支持系统看板。"""
        url = f"{self.endpoint}/v4/monitor/monitor-board/delete-sys-resources"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorMonitorBoardDeleteSysResourcesResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v41_monitor_query_contact_groups(self, request: V41MonitorQueryContactGroupsRequest) -> V41MonitorQueryContactGroupsResponse:
        """调用此接口可查询告警联系人组的列表。"""
        url = f"{self.endpoint}/v4.1/monitor/query-contact-groups"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V41MonitorQueryContactGroupsResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_describe_contact_group(self, request: V4MonitorDescribeContactGroupRequest) -> V4MonitorDescribeContactGroupResponse:
        """调用此接口可查询告警联系人组的配置详情。"""
        url = f"{self.endpoint}/v4/monitor/describe-contact-group"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorDescribeContactGroupResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_update_contact_group(self, request: V4MonitorUpdateContactGroupRequest) -> V4MonitorUpdateContactGroupResponse:
        """调用此接口可修改告警联系组基本信息， 支持全量字段修改。"""
        url = f"{self.endpoint}/v4/monitor/update-contact-group"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorUpdateContactGroupResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_delete_contact_groups(self, request: V4MonitorDeleteContactGroupsRequest) -> V4MonitorDeleteContactGroupsResponse:
        """调用此接口可批量删除多个删除告警联系人组。"""
        url = f"{self.endpoint}/v4/monitor/delete-contact-groups"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorDeleteContactGroupsResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_update_group_contacts(self, request: V4MonitorUpdateGroupContactsRequest) -> V4MonitorUpdateGroupContactsResponse:
        """调用此接口可变更告警联系组内的告警联系人列表。"""
        url = f"{self.endpoint}/v4/monitor/update-group-contacts"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorUpdateGroupContactsResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_delete_contact_group(self, request: V4MonitorDeleteContactGroupRequest) -> V4MonitorDeleteContactGroupResponse:
        """调用此接口可删除告警联系人组。"""
        url = f"{self.endpoint}/v4/monitor/delete-contact-group"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorDeleteContactGroupResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_create_contact_group(self, request: V4MonitorCreateContactGroupRequest) -> V4MonitorCreateContactGroupResponse:
        """调用此接口可创建告警联系组。"""
        url = f"{self.endpoint}/v4/monitor/create-contact-group"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorCreateContactGroupResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_activate_contact(self, request: V4MonitorActivateContactRequest) -> V4MonitorActivateContactResponse:
        """调用此接口可激活告警联系人的手机短息或邮箱，激活后的媒介可接收平台告警信息。"""
        url = f"{self.endpoint}/v4/monitor/activate-contact"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorActivateContactResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v41_monitor_query_contacts(self, request: V41MonitorQueryContactsRequest) -> V41MonitorQueryContactsResponse:
        """调用此接口可查询告警联系人的列表。"""
        url = f"{self.endpoint}/v4.1/monitor/query-contacts"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V41MonitorQueryContactsResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_describe_contact(self, request: V4MonitorDescribeContactRequest) -> V4MonitorDescribeContactResponse:
        """调用此接口可查看告警联系人的配置详情。"""
        url = f"{self.endpoint}/v4/monitor/describe-contact"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorDescribeContactResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_delete_contacts(self, request: V4MonitorDeleteContactsRequest) -> V4MonitorDeleteContactsResponse:
        """调用此接口可批量删除多个创建告警联系人。"""
        url = f"{self.endpoint}/v4/monitor/delete-contacts"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorDeleteContactsResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_contact_activation_code(self, request: V4MonitorContactActivationCodeRequest) -> V4MonitorContactActivationCodeResponse:
        """调用此接口可对告警联系人发送手机短息激活验证码或邮箱激活验证码。"""
        url = f"{self.endpoint}/v4/monitor/contact-activation-code"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorContactActivationCodeResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_delete_contact(self, request: V4MonitorDeleteContactRequest) -> V4MonitorDeleteContactResponse:
        """调用此接口可删除告警联系人。"""
        url = f"{self.endpoint}/v4/monitor/delete-contact"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorDeleteContactResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_create_contact(self, request: V4MonitorCreateContactRequest) -> V4MonitorCreateContactResponse:
        """调用此接口可创建告警联系人，用于告警通知。"""
        url = f"{self.endpoint}/v4/monitor/create-contact"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorCreateContactResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_update_contacts(self, request: V4MonitorUpdateContactsRequest) -> V4MonitorUpdateContactsResponse:
        """调用此接口可修改告警联系人配置，支持全量字段修改。"""
        url = f"{self.endpoint}/v4/monitor/update-contacts"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorUpdateContactsResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_monitor_board_describe_view(self, request: V4MonitorMonitorBoardDescribeViewRequest) -> V4MonitorMonitorBoardDescribeViewResponse:
        """查看监控看板详细信息，包括视图信息，不包含监控数据信息。"""
        url = f"{self.endpoint}/v4/monitor/monitor-board/describe-view"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorMonitorBoardDescribeViewResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_monitor_board_describe(self, request: V4MonitorMonitorBoardDescribeRequest) -> V4MonitorMonitorBoardDescribeResponse:
        """查看监控看板详细信息，包括视图信息，不包含监控数据信息。"""
        url = f"{self.endpoint}/v4/monitor/monitor-board/describe"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorMonitorBoardDescribeResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_monitor_board_update_view(self, request: V4MonitorMonitorBoardUpdateViewRequest) -> V4MonitorMonitorBoardUpdateViewResponse:
        """更新已有监控视图。"""
        url = f"{self.endpoint}/v4/monitor/monitor-board/update-view"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorMonitorBoardUpdateViewResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_monitor_board_create_view(self, request: V4MonitorMonitorBoardCreateViewRequest) -> V4MonitorMonitorBoardCreateViewResponse:
        """为已存在的监控看板创建视图。"""
        url = f"{self.endpoint}/v4/monitor/monitor-board/create-view"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorMonitorBoardCreateViewResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_monitor_monitor_board_create(self, request: V4MonitorMonitorBoardCreateRequest) -> V4MonitorMonitorBoardCreateResponse:
        """创建监控看板，可以创建空看板，也可以附带视图创建。"""
        url = f"{self.endpoint}/v4/monitor/monitor-board/create"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4MonitorMonitorBoardCreateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))



