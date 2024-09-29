### semantics of JVM

- The Values
  - local values $V_{\lambda}$ := (int n) | (float f) | (ref f)
  - stack values $V_{\sigma}$ := (byte b) | (char c) | (short s) | $V_{\lambda}$
  - heap values $V_{\eta}$ := (array n t a) | (class cn f s) | $V_{\sigma}$

- The context
  - we need a program counter $\iota$ so that we can use bc[$\iota$] to get the bytecode at the current position


