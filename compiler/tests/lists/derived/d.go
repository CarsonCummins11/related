package derived

import "strings"

func Times2(a int) int {
	return a * 2
}
func Times2_all(a []int) []int {
	b := make([]int, len(a))
	for i, v := range a {
		b[i] = Times2(v)
	}
	return b
}
func Capitalize(a string) string {
	return strings.ToUpper(a)
}

func Capitalize_all(a []string) []string {
	b := make([]string, len(a))
	for i, v := range a {
		b[i] = Capitalize(v)
	}
	return b
}
