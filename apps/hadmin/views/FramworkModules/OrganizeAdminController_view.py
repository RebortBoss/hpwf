# _*_ coding: utf-8 _*_
__author__ = 'seesky@hstecs.com'
__date__ = '2019/1/8 16:15'

from apps.hadmin.MvcAppUtilties.AjaxOnly import AjaxOnly
from apps.hadmin.MvcAppUtilties.LoginAuthorize import LoginAuthorize

from apps.bizlogic.service.base.OrganizeService import OrganizeService
from apps.bizlogic.service.permission.ScopPermission import ScopPermission

from apps.utilities.publiclibrary.SystemInfo import SystemInfo
from apps.utilities.message.OrganizeCategory import OrganizeCategory
from apps.hadmin.MvcAppUtilties.CommonUtils import CommonUtils

from django.db.models import Q
from django.http.response import HttpResponse

from django.template import loader ,Context
from apps.hadmin.MvcAppUtilties.PublicController import PublicController

from apps.utilities.publiclibrary.SystemInfo import SystemInfo

def GetOrganizeScope(userInfo, permissionItemScopeCode, isInnerOrganize):
    """
    获取组织机构权限域数据
    Args:
    Returns:
    """
    if userInfo.IsAdministrator or (not permissionItemScopeCode) or (not SystemInfo.EnableUserAuthorizationScope):
        dataTable = OrganizeService.GetDT(object)
    else:
        dataTable = ScopPermission.GetOrganizeDTByPermissionScope(None, userInfo, userInfo.Id, permissionItemScopeCode)

    if isInnerOrganize:
        dataTable = dataTable.filter(Q(isinnerorganize='1')).order_by('sortcode')
    return dataTable

def GroupJsondata(groups, parentId):
    treeLevel = 0
    sb = ""
    list = []
    for g in groups:
        if g.parentid == parentId:
            list.append(g)
    for g in list:
        treeLevel = treeLevel + 1
        #jsons = json.dumps(g)
        #jsons = serializers.serialize('json', g)
        jsons = g.toJSON()
        jsons = jsons.rstrip('}')
        sb = sb + jsons
        if g.category and g.category.lower() == OrganizeCategory.OrganizeCategory.get('Company').lower():
            sb = sb + ",\"iconCls\":\"icon16_sitemap\""
        elif g.category and g.category.lower() == OrganizeCategory.OrganizeCategory.get('SubCompany').lower():
            sb = sb + ",\"iconCls\":\"icon16_server\""
        elif g.category and g.category.lower() == OrganizeCategory.OrganizeCategory.get('Department').lower():
            sb = sb + ",\"iconCls\":\"icon16_building\""
        elif g.category and g.category.lower() == OrganizeCategory.OrganizeCategory.get('SubDepartment').lower():
            sb = sb + ",\"iconCls\":\"icon16_ipod\""
        elif g.category and g.category.lower() == OrganizeCategory.OrganizeCategory.get('Workgroup').lower():
            sb = sb + ",\"iconCls\":\"icon16_envelopes\""

        sb = sb + ","

        if treeLevel >= 2 and len(groups.filter(Q(parentid=g.id))) > 0:
            sb = sb + "\"state\":\"closed\","

        sb = sb + "\"children\":["

        if g.id:
            sb = sb + GroupJsondata(groups, g.id)
        sb = sb + "]},"
    sb = sb.rstrip(',')
    return sb

@LoginAuthorize
def GetOrganizeTreeJson(request):

    try:
        isTree = request.GET['isTree']
        if isTree == '1':
            isTree = True
        else:
            isTree = False
    except:
        isTree = False





    response = HttpResponse()
    dtOrganize = GetOrganizeScope(CommonUtils.Current(response, request), 'Resource.ManagePermission', False)
    dataTable = CommonUtils.CheckTreeParentId(dtOrganize, 'id', 'parentid')
    organizeJson = "[" + GroupJsondata(dtOrganize, "#") + "]"

    if isTree:
        response.content = organizeJson.replace("fullname", "text")
        return response
    else:
        response.content = organizeJson
        return response

def BuildToolBarButton(response, request):
    sb = ''
    linkbtnTemplate = "<a id=\"a_{0}\" class=\"easyui-linkbutton\" style=\"float:left\"  plain=\"true\" href=\"javascript:;\" icon=\"{1}\"  {2} title=\"{3}\">{4}</a>"
    sb = sb + "<a id=\"a_refresh\" class=\"easyui-linkbutton\" style=\"float:left\"  plain=\"true\" href=\"javascript:;\" icon=\"icon16_arrow_refresh\"  title=\"重新加载\">刷新</a> "
    sb = sb + "<div class='datagrid-btn-separator'></div> "
    sb = sb + linkbtnTemplate.format("Add", "icon16_add", "" if PublicController.IsAuthorized(response, request, "OrganizeManagement.Add") else "disabled=\"True\"", "新增组织机构", "新增")
    sb = sb + linkbtnTemplate.format("Edit", "icon16_edit_button", "" if PublicController.IsAuthorized(response, request, "OrganizeManagement.Edit") else "disabled=\"True\"", "修改选中的组织机构", "修改")
    sb = sb + linkbtnTemplate.format("Delete", "icon16_delete", "" if PublicController.IsAuthorized(response, request, "OrganizeManagement.Delete") else "disabled=\"True\"", "删除选中组织机构", "删除")
    sb = sb + "<div class='datagrid-btn-separator'></div> "
    sb = sb + linkbtnTemplate.format("MoveTo", "icon16_arrow_switch", "" if PublicController.IsAuthorized(response, request, "OrganizeManagement.Move") else "disabled=\"True\"", "移动选中的组织机构", "移动")
    sb = sb + linkbtnTemplate.format("Export", "icon16_export_excel", "" if PublicController.IsAuthorized(response, request, "OrganizeManagement.Export") else "disabled=\"True\"", "导出组织机构数据", "导出")
    if SystemInfo.EnableOrganizePermission:
        sb = sb + "<div class='datagrid-btn-separator'></div> "
        sb = sb + linkbtnTemplate.format("UserOrganizePermission", "icon16_key", "" if PublicController.IsAuthorized(response, request, "OrganizeManagement.UserOrganizePermission") else "disabled=\"True\"", "设置用户组织机构权限", "用户组织机构权限")
        sb = sb + linkbtnTemplate.format("RoleOrganizePermission", "icon16_lightning", "" if PublicController.IsAuthorized(response, request, "OrganizeManagement.RolerOrganizePermission") else "disabled=\"True\"", "设置角色组织机构权限", "角色组织机构权限")
    return sb

@LoginAuthorize
def Index(request):
    """
        起始页
        Args:
        Returns:
        """
    response = HttpResponse()
    tmp = loader.get_template('OrganizeAdmin/Index.html')  # 加载模板
    render_content = {'Skin': CommonUtils.Theme(response, request),
                      'ToolButton': BuildToolBarButton(response, request)}  # 将要渲染到模板的数据
    new_body = tmp.render(render_content)  # 渲染模板
    response.content = new_body  # 设置返回内容
    return response