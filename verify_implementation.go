package main

import (
	"fmt"
	"log"

	C "github.com/metacubex/mihomo/constant"
	"github.com/metacubex/mihomo/rules"
	RC "github.com/metacubex/mihomo/rules/common"
)

func main() {
	fmt.Println("=== 验证 PROXY-USER 规则实现 ===")

	// 1. 测试规则创建
	fmt.Println("\n1. 测试规则创建...")
	rule, err := RC.NewProxyUser("feifeimao/vipuser", "VIP_PROXY")
	if err != nil {
		log.Fatalf("创建规则失败: %v", err)
	}
	fmt.Printf("✓ 规则创建成功: %s -> %s\n", rule.Payload(), rule.Adapter())

	// 2. 测试规则类型
	fmt.Println("\n2. 测试规则类型...")
	if rule.RuleType() != C.ProxyUser {
		log.Fatalf("规则类型错误: 期望 %v, 实际 %v", C.ProxyUser, rule.RuleType())
	}
	fmt.Printf("✓ 规则类型正确: %s\n", rule.RuleType().String())

	// 3. 测试规则匹配
	fmt.Println("\n3. 测试规则匹配...")

	// 创建测试元数据
	testCases := []struct {
		user     string
		expected bool
		desc     string
	}{
		{"feifeimao", true, "VIP用户 feifeimao"},
		{"vipuser", true, "VIP用户 vipuser"},
		{"normaluser", false, "普通用户 normaluser"},
		{"", false, "空用户名"},
	}

	for _, tc := range testCases {
		metadata := &C.Metadata{
			InUser: tc.user,
		}

		matched, adapter := rule.Match(metadata, C.RuleMatchHelper{})
		if matched != tc.expected {
			log.Fatalf("匹配结果错误 [%s]: 期望 %v, 实际 %v", tc.desc, tc.expected, matched)
		}

		if matched && adapter != "VIP_PROXY" {
			log.Fatalf("适配器错误 [%s]: 期望 VIP_PROXY, 实际 %s", tc.desc, adapter)
		}

		status := "✗"
		if matched {
			status = "✓"
		}
		fmt.Printf("%s %s: 用户='%s', 匹配=%v, 适配器='%s'\n",
			status, tc.desc, tc.user, matched, adapter)
	}

	// 4. 测试规则解析
	fmt.Println("\n4. 测试规则解析...")
	parsedRule, err := rules.ParseRule("PROXY-USER", "testuser", "TEST_PROXY", nil, nil)
	if err != nil {
		log.Fatalf("解析规则失败: %v", err)
	}

	if parsedRule.RuleType() != C.ProxyUser {
		log.Fatalf("解析的规则类型错误: 期望 %v, 实际 %v", C.ProxyUser, parsedRule.RuleType())
	}

	if parsedRule.Adapter() != "TEST_PROXY" {
		log.Fatalf("解析的适配器错误: 期望 TEST_PROXY, 实际 %s", parsedRule.Adapter())
	}

	fmt.Printf("✓ 规则解析成功: %s -> %s\n", parsedRule.Payload(), parsedRule.Adapter())

	// 5. 测试多用户解析
	fmt.Println("\n5. 测试多用户解析...")
	multiUserRule, err := rules.ParseRule("PROXY-USER", "user1/user2/user3", "MULTI_PROXY", nil, nil)
	if err != nil {
		log.Fatalf("解析多用户规则失败: %v", err)
	}

	// 测试多用户匹配
	users := []string{"user1", "user2", "user3", "user4"}
	expected := []bool{true, true, true, false}

	for i, user := range users {
		metadata := &C.Metadata{InUser: user}
		matched, _ := multiUserRule.Match(metadata, C.RuleMatchHelper{})

		if matched != expected[i] {
			log.Fatalf("多用户匹配错误 [%s]: 期望 %v, 实际 %v", user, expected[i], matched)
		}

		status := "✗"
		if matched {
			status = "✓"
		}
		fmt.Printf("%s 用户 '%s': 匹配=%v\n", status, user, matched)
	}

	fmt.Println("\n=== 所有测试通过! ===")
	fmt.Println("\n使用方法:")
	fmt.Println("1. 编译: go build -o mihomo-custom.exe .")
	fmt.Println("2. 运行: mihomo-custom.exe -f proxy_user_config.yaml")
	fmt.Println("3. 测试: python test_proxy_user.py")
}
