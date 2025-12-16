import thriftpy2 as thriftpy
import six

api_description = """
struct Query_Response {
    1:required bool status,
    2:optional string msg,
    5:optional string error
}

struct Query_Request {
    1:required string method_name,
    2:required binary params,
    3:required string token,
    4:required string audience,
}

struct Submit_Request {
    1:required string strategy_code,
    2:required binary params,
    3:required binary data,
}

service DataService {
    string ping(),
    Query_Response query(1:Query_Request req),
    Query_Response auth(1:string username, 2:string password, 5:bool compress, 8:string mac, 10:string version),
    Query_Response auth_by_token(1:string token, 2:string audience),
    Query_Response submit(1:Submit_Request req)
}
"""
thrift = thriftpy.load_fp(six.StringIO(api_description), "api_thrift")
