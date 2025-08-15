package common

import (
	"fmt"
	"strings"

	C "github.com/metacubex/mihomo/constant"
)

type ProxyUser struct {
	*Base
	users   []string
	adapter string
	payload string
}

func (p *ProxyUser) Match(metadata *C.Metadata, helper C.RuleMatchHelper) (bool, string) {
	// 添加调试日志
	//fmt.Printf("[DEBUG] ProxyUser.Match called: InUser=%s, ExpectedUsers=%v\n",
	//	metadata.InUser, p.users)

	// 检查代理认证用户名是否匹配 (users配置文件解析得到的，metadata.InUser是请求携带的ProxyUser数据)
	for _, user := range p.users {
		if metadata.InUser == user {
			fmt.Printf("[DEBUG] ProxyUser.Match: MATCHED! User %s using adapter %s\n", user, p.adapter)
			return true, p.adapter
		}
	}

	//fmt.Printf("[DEBUG] ProxyUser.Match: No match found for user %s\n", metadata.InUser)
	return false, ""
}

func (p *ProxyUser) RuleType() C.RuleType {
	return C.ProxyUser
}

func (p *ProxyUser) Adapter() string {
	return p.adapter
}

func (p *ProxyUser) Payload() string {
	return p.payload
}

func NewProxyUser(users, adapter string) (*ProxyUser, error) {
	userList := strings.Split(users, "/")
	for i, user := range userList {
		user = strings.TrimSpace(user) // 等效Python strip，过滤空格之类
		if len(user) == 0 {
			return nil, fmt.Errorf("proxy user couldn't be empty")
		}
		userList[i] = user
		fmt.Printf("[DEBUG] ProxyUser.Inset: 从配置文件注入ProxyUser: %v \n", user)
	}

	return &ProxyUser{
		Base:    &Base{},
		users:   userList,
		adapter: adapter,
		payload: users,
	}, nil
}
