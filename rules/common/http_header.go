package common

import (
	"fmt"
	"strings"

	C "github.com/metacubex/mihomo/constant"
)

type HTTPHeader struct {
	*Base
	headerKey   string
	headerValue string
	adapter     string
}

func (h *HTTPHeader) RuleType() C.RuleType {
	return C.HTTPHeader
}

func (h *HTTPHeader) Match(metadata *C.Metadata, helper C.RuleMatchHelper) (bool, string) {
	// 添加调试日志
	fmt.Printf("[DEBUG] HTTPHeader.Match called: Type=%s, HeaderKey=%s, HeaderValue=%s\n", 
		metadata.Type.String(), h.headerKey, h.headerValue)
	
	// 只对 HTTP/HTTPS 请求进行匹配
	if metadata.Type != C.HTTP && metadata.Type != C.HTTPS {
		fmt.Printf("[DEBUG] HTTPHeader.Match: Not HTTP/HTTPS request, skipping\n")
		return false, ""
	}

	// 检查是否有 HTTP 请求头信息
	if metadata.HTTPHeaders == nil {
		fmt.Printf("[DEBUG] HTTPHeader.Match: No HTTP headers found\n")
		return false, ""
	}

	fmt.Printf("[DEBUG] HTTPHeader.Match: Available headers: %+v\n", metadata.HTTPHeaders)

	// 检查指定的请求头是否存在且匹配
	if value, exists := metadata.HTTPHeaders[h.headerKey]; exists {
		fmt.Printf("[DEBUG] HTTPHeader.Match: Found header %s=%s\n", h.headerKey, value)
		if h.headerValue == "" || strings.EqualFold(value, h.headerValue) {
			fmt.Printf("[DEBUG] HTTPHeader.Match: MATCHED! Using adapter %s\n", h.adapter)
			return true, h.adapter
		}
		fmt.Printf("[DEBUG] HTTPHeader.Match: Header value doesn't match expected value\n")
	} else {
		fmt.Printf("[DEBUG] HTTPHeader.Match: Header %s not found\n", h.headerKey)
	}

	return false, ""
}

func (h *HTTPHeader) Adapter() string {
	return h.adapter
}

func (h *HTTPHeader) Payload() string {
	if h.headerValue == "" {
		return h.headerKey
	}
	return h.headerKey + ":" + h.headerValue
}

func NewHTTPHeader(headerKey, headerValue, adapter string) (*HTTPHeader, error) {
	return &HTTPHeader{
		Base:        &Base{},
		headerKey:   headerKey,
		headerValue: headerValue,
		adapter:     adapter,
	}, nil
}