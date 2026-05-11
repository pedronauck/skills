---
name: storybook
description: "Storybook 스토리 작성 및 CSF 3.0 베스트 프랙티스 스킬. 다음 상황에서 사용: (1) 새 스토리 파일(.stories.tsx, .stories.ts) 작성 시, (2) 기존 스토리 수정 시, (3) Args, Decorators, Parameters 설정 시, (4) Storybook 설정 파일(.storybook/) 작업 시, (5) 'story', 'stories', 'storybook', 'CSF' 키워드가 포함된 작업 시"
license: MIT
metadata:
  author: DaleStudy
  version: "1.1.0"
---

# Storybook

## 모범 관례

### 1. CSF 3.0 형식 사용

최신 Component Story Format 3.0 사용. 더 간결하고 타입 안전.

```tsx
// ❌ CSF 2.0 (구형)
export default {
  title: "Components/Button",
  component: Button,
};

export const Primary = () => <Button variant="primary">Click me</Button>;

// ✅ CSF 3.0 (권장)
import type { Meta, StoryObj } from "@storybook/react";
import { Button } from "./Button";

const meta = {
  component: Button,
  tags: ["autodocs"], // 자동 문서 생성
  args: {
    variant: "primary",
    children: "Click me",
  },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Primary: Story = {};

export const Secondary: Story = {
  args: {
    variant: "secondary",
  },
};
```

### 2. Args 기반 스토리 작성

컴포넌트 Props를 Args로 정의하여 Controls 패널에서 인터랙티브하게 조작 가능.

- **기본값은 `args`에서 선언** (❌ `argTypes.defaultValue` 사용 금지). Meta의 `args`에 기본값을 두면 Controls 패널에서 자동으로 해당 값이 선택됨
- **여러 스토리에 공통으로 필요한 args는 Meta(컴포넌트) 수준에서 선언**하고, 개별 스토리에서는 차이점만 오버라이드

```tsx
// ❌ 하드코딩된 Props
export const Disabled: Story = {
  render: () => <Button disabled>Disabled</Button>,
};

// ❌ 여러 스토리에서 같은 args 중복
export const Primary: Story = {
  args: { children: "Click me", variant: "primary" },
};
export const Secondary: Story = {
  args: { children: "Click me", variant: "secondary" },
};

// ✅ Meta에서 공통 args 선언, 스토리에서 차이점만 오버라이드
const meta = {
  component: Button,
  args: {
    children: "Click me",
    variant: "primary",
  },
} satisfies Meta<typeof Button>;

export const Primary: Story = {};

export const Secondary: Story = {
  args: { variant: "secondary" },
};

export const Disabled: Story = {
  args: { disabled: true },
};
```

### 3. title 생략 — 파일 경로 기반 자동 추론

`title`을 문자열로 직접 명시하면 타입 안전하지 않고, 컴포넌트 이름/경로 변경 시 싱크가 깨지기 쉬움. Storybook은 파일 경로에서 사이드바 계층을 자동 추론하므로 `title` 생략.

```tsx
// ❌ title 직접 명시 — 타입 안전하지 않고 싱크 깨짐 위험
const meta = {
  title: "Components/Button",
  component: Button,
} satisfies Meta<typeof Button>;

// ✅ title 생략 — 파일 경로에서 자동 추론
const meta = {
  component: Button,
} satisfies Meta<typeof Button>;
```

### 4. 타입 안전한 Meta 정의

`satisfies` 키워드로 타입 체크와 타입 추론 동시 활용.

```tsx
// ❌ 타입 추론 불가
const meta: Meta<typeof Button> = {
  component: Button,
};

// ✅ 타입 체크와 추론 모두 가능
const meta = {
  component: Button,
  args: {
    size: "md",
    variant: "primary",
  },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;
```

### 5. Decorators로 컨텍스트 제공

공통 래퍼나 Provider를 Decorator로 적용.

```tsx
// 개별 스토리에 Decorator 적용
export const WithTheme: Story = {
  decorators: [
    Story => (
      <ThemeProvider theme="dark">
        <Story />
      </ThemeProvider>
    ),
  ],
};

// 모든 스토리에 Decorator 적용
const meta = {
  component: Button,
  decorators: [
    Story => (
      <div style={{ padding: "3rem" }}>
        <Story />
      </div>
    ),
  ],
} satisfies Meta<typeof Button>;
```

### 6. Parameters로 동작 커스터마이즈

```tsx
const meta = {
  component: Button,
  parameters: {
    layout: "centered", // 스토리를 중앙 정렬
    backgrounds: {
      default: "light",
      values: [
        { name: "light", value: "#ffffff" },
        { name: "dark", value: "#000000" },
      ],
    },
  },
} satisfies Meta<typeof Button>;

// 개별 스토리에서 오버라이드
export const OnDark: Story = {
  parameters: {
    backgrounds: { default: "dark" },
  },
};
```

### 7. ArgTypes — 자동 추론 우선, 수동 지정 최소화

Storybook은 컴포넌트 함수의 TypeScript 타입에서 최적의 argType을 자동 적용함. 수동으로 덮어쓰면 컴포넌트 타입 변경 시마다 argType 싱크를 맞춰야 하므로 **타당한 이유 없이 argType을 직접 지정하지 않음**.

**수동 지정이 타당한 경우:**

- `ReactNode` 타입인데 Controls에서 텍스트 입력이 필요할 때 → `control: 'text'`
- Compound pattern (컴포넌트를 여러 개 export) → argTypes로 명시
- 특정 스토리에서 항상 고정되어야 하는 prop → `control: false`

```tsx
// ❌ 불필요한 argType 수동 지정 — 타입 변경 시 싱크 깨짐
const meta = {
  component: Button,
  argTypes: {
    variant: {
      control: "select",
      options: ["primary", "secondary", "tertiary"],
    },
    size: {
      control: "radio",
      options: ["sm", "md", "lg"],
    },
    disabled: {
      control: "boolean",
    },
  },
} satisfies Meta<typeof Button>;

// ✅ 자동 추론에 맡기고, 필요한 경우만 수동 지정
const meta = {
  component: Button,
  argTypes: {
    // ReactNode 타입이지만 텍스트 입력이 필요한 경우
    children: { control: "text" },
  },
} satisfies Meta<typeof Button>;

// ✅ 특정 스토리에서 prop을 고정할 때 — control: false
export const Horizontal: Story = {
  args: { orientation: "horizontal" },
  argTypes: {
    orientation: { control: false }, // 이 스토리에서는 항상 horizontal
  },
};
```

## 권장 스토리 구조

```tsx
import type { Meta, StoryObj } from "@storybook/react";
import { Button } from "./Button";

// 1. Meta 정의 — title 생략, 공통 args 선언, argTypes는 자동 추론에 위임
const meta = {
  component: Button,
  tags: ["autodocs"],
  parameters: {
    layout: "centered",
  },
  args: {
    children: "Button",
    size: "md",
    variant: "primary",
  },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

// 2. 기본 스토리 — Meta args를 그대로 사용
export const Primary: Story = {};

// 3. 변형 스토리들 — 차이점만 오버라이드
export const Secondary: Story = {
  args: {
    variant: "secondary",
  },
};

export const Disabled: Story = {
  args: {
    disabled: true,
  },
};

// 4. prop 고정이 필요한 스토리 — control: false 사용
export const Horizontal: Story = {
  args: { orientation: "horizontal" },
  argTypes: {
    orientation: { control: false },
  },
};

// 5. 복잡한 상태나 컨텍스트가 필요한 경우
export const WithCustomTheme: Story = {
  decorators: [
    Story => (
      <ThemeProvider theme="custom">
        <Story />
      </ThemeProvider>
    ),
  ],
};
```

## ArgTypes 수동 지정이 필요한 경우 참고

> **원칙:** 대부분의 argType은 Storybook이 컴포넌트 타입에서 자동 추론. 아래는 자동 추론이 부적절할 때만 사용.
>
> **기본값은 `argTypes.defaultValue`가 아닌 `args`에서 선언.**

```tsx
argTypes: {
  // ReactNode 타입이지만 텍스트 입력이 필요할 때
  children: { control: 'text' },

  // Range slider (자동 추론이 적절하지 않을 때)
  opacity: {
    control: { type: 'range', min: 0, max: 1, step: 0.1 },
  },

  // Action logger (이벤트 핸들러)
  onClick: { action: 'clicked' },

  // Control 비활성화 (특정 스토리에서 prop 고정)
  orientation: { control: false },
}
```

## 자주 사용되는 Parameters

```tsx
parameters: {
  // 레이아웃 설정
  layout: 'centered' | 'fullscreen' | 'padded',

  // 배경 설정
  backgrounds: {
    default: 'light',
    values: [
      { name: 'light', value: '#ffffff' },
      { name: 'dark', value: '#333333' },
    ],
  },

  // Actions 패널 설정
  actions: {
    argTypesRegex: '^on[A-Z].*', // on으로 시작하는 Props 자동 감지
  },

  // Docs 설정
  docs: {
    description: {
      component: '버튼 컴포넌트 상세 설명',
    },
  },
}
```

## Decorators 패턴

```tsx
// 1. 스타일 래퍼
(Story) => (
  <div style={{ padding: '3rem' }}>
    <Story />
  </div>
)

// 2. Theme Provider
(Story) => (
  <ThemeProvider theme="dark">
    <Story />
  </ThemeProvider>
)

// 3. Router Provider (React Router 사용 시)
(Story) => (
  <MemoryRouter initialEntries={['/']}>
    <Story />
  </MemoryRouter>
)

// 4. 다국어 Provider
(Story) => (
  <I18nProvider locale="ko">
    <Story />
  </I18nProvider>
)

// 5. 전역 상태 Provider
(Story) => (
  <Provider store={mockStore}>
    <Story />
  </Provider>
)
```

## 파일 명명 규칙

```
Component.tsx           # 컴포넌트 구현
Component.stories.tsx   # 스토리 파일 (같은 디렉토리)
Component.test.tsx      # 테스트 파일
```

## Storybook 설정 파일

```typescript
// .storybook/main.ts
import type { StorybookConfig } from "@storybook/react-vite";

const config: StorybookConfig = {
  stories: ["../src/**/*.stories.@(ts|tsx)"],
  addons: [
    "@storybook/addon-essentials", // Controls, Actions, Docs 등
    "@storybook/addon-interactions", // Play functions
  ],
  framework: {
    name: "@storybook/react-vite",
    options: {},
  },
};

export default config;
```

```typescript
// .storybook/preview.ts
import type { Preview } from '@storybook/react';

const preview: Preview = {
  parameters: {
    actions: { argTypesRegex: '^on[A-Z].*' },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/,
      },
    },
  },
  // 모든 스토리에 적용될 전역 Decorators
  decorators: [
    (Story) => (
      <div style={{ fontFamily: 'Arial, sans-serif' }}>
        <Story />
      </div>
    ),
  ],
};

export default preview;
```
