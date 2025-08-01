package inbound

import (
	"net"
	"net/http"

	C "github.com/metacubex/mihomo/constant"
	"github.com/metacubex/mihomo/transport/socks5"
)

// NewHTTP receive normal http request and return HTTPContext
func NewHTTP(target socks5.Addr, srcConn net.Conn, conn net.Conn, additions ...Addition) (net.Conn, *C.Metadata) {
	metadata := parseSocksAddr(target)
	metadata.NetWork = C.TCP
	metadata.Type = C.HTTP
	metadata.RawSrcAddr = srcConn.RemoteAddr()
	metadata.RawDstAddr = srcConn.LocalAddr()
	ApplyAdditions(metadata, WithSrcAddr(srcConn.RemoteAddr()), WithInAddr(srcConn.LocalAddr()))
	ApplyAdditions(metadata, additions...)
	return conn, metadata
}

// NewHTTPWithHeaders receive normal http request with headers and return HTTPContext
func NewHTTPWithHeaders(target socks5.Addr, srcConn net.Conn, conn net.Conn, headers http.Header, additions ...Addition) (net.Conn, *C.Metadata) {
	metadata := parseSocksAddr(target)
	metadata.NetWork = C.TCP
	metadata.Type = C.HTTP
	metadata.RawSrcAddr = srcConn.RemoteAddr()
	metadata.RawDstAddr = srcConn.LocalAddr()
	
	// 提取 HTTP 请求头
	if headers != nil {
		metadata.HTTPHeaders = make(map[string]string)
		for key, values := range headers {
			if len(values) > 0 {
				metadata.HTTPHeaders[key] = values[0] // 只取第一个值
			}
		}
	}
	
	ApplyAdditions(metadata, WithSrcAddr(srcConn.RemoteAddr()), WithInAddr(srcConn.LocalAddr()))
	ApplyAdditions(metadata, additions...)
	return conn, metadata
}
