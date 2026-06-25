# OCR Invoice Processing Monorepo Implementation Plan

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Build a monorepo containing a Spring Boot backend and a Next.js frontend to extract structured JSON data from invoice images using the Gemini Vision API.

**Architecture:** A Next.js frontend allows users to upload invoice images, which are sent via REST to a Spring Boot backend. The backend forwards the image to the Gemini Vision API using a structured schema and validates the mathematically calculated amounts before saving to PostgreSQL and returning the JSON to the client.

**Tech Stack:** Java 17+, Spring Boot 3.x, Maven, Next.js 14+ (App Router), TypeScript, Gemini API (Google AI Client / REST API).

---

### Task 1: Initialize Backend Project Structure

**Files:**
- Create: `backend/pom.xml`
- Create: `backend/src/main/java/com/example/ocr/OcrApplication.java`
- Create: `backend/src/main/resources/application.yml`
- Test: `backend/src/test/java/com/example/ocr/OcrApplicationTests.java`

**Step 1: Write a minimal failing test**
Create `backend/src/test/java/com/example/ocr/OcrApplicationTests.java`:
```java
package com.example.ocr;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class OcrApplicationTests {
    @Test
    void contextLoads() {
    }
}
```

**Step 2: Run test to verify it fails**
Run: `mvn -f backend/pom.xml test`
Expected: FAIL (because POM and Application files are not yet created or configured).

**Step 3: Write minimal implementation**
Create `backend/pom.xml` with Spring Boot dependencies and `backend/src/main/java/com/example/ocr/OcrApplication.java`:
```java
package com.example.ocr;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class OcrApplication {
    public static void main(String[] args) {
        SpringApplication.run(OcrApplication.class, args);
    }
}
```
Create `backend/src/main/resources/application.yml` with empty config.

**Step 4: Run test to verify it passes**
Run: `mvn -f backend/pom.xml test`
Expected: PASS (exit code 0, test context loads successfully).

**Step 5: Commit**
```bash
git add backend/
git commit -m "feat: initialize backend spring boot project structure"
```

---

### Task 2: Create Basic Rest Controller (Ping Endpoint)

**Files:**
- Create: `backend/src/main/java/com/example/ocr/controller/PingController.java`
- Test: `backend/src/test/java/com/example/ocr/controller/PingControllerTest.java`

**Step 1: Write the failing test**
Create `backend/src/test/java/com/example/ocr/controller/PingControllerTest.java`:
```java
package com.example.ocr.controller;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(PingController.class)
class PingControllerTest {
    @Autowired
    private MockMvc mockMvc;

    @Test
    void testPing() throws Exception {
        mockMvc.perform(get("/api/ping"))
            .andExpect(status().isOk())
            .andExpect(content().string("pong"));
    }
}
```

**Step 2: Run test to verify it fails**
Run: `mvn -f backend/pom.xml test -Dtest=PingControllerTest`
Expected: FAIL (Compilation error or 404 because controller doesn't exist).

**Step 3: Write minimal implementation**
Create `backend/src/main/java/com/example/ocr/controller/PingController.java`:
```java
package com.example.ocr.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class PingController {
    @GetMapping("/ping")
    public String ping() {
        return "pong";
    }
}
```

**Step 4: Run test to verify it passes**
Run: `mvn -f backend/pom.xml test -Dtest=PingControllerTest`
Expected: PASS

**Step 5: Commit**
```bash
git add backend/src/main/java/com/example/ocr/controller/PingController.java backend/src/test/java/com/example/ocr/controller/PingControllerTest.java
git commit -m "feat: add basic ping endpoint"
```

---

### Task 3: Initialize Next.js Frontend Project Structure

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/src/app/page.tsx`
- Create: `frontend/src/app/layout.tsx`

**Step 1: Write a failing test**
Create a small smoke test in `frontend/src/app/page.test.tsx` (using Jest/Vitest or simple script validation if test runner not ready):
```typescript
import { render, screen } from '@testing-library/react';
import Page from './page';

test('renders OCR header', () => {
  render(<Page />);
  expect(screen.getByText(/OCR Invoice Processing/i)).toBeInTheDocument();
});
```

**Step 2: Run test to verify it fails**
Run: `npm --prefix frontend test` (or equivalent run command)
Expected: FAIL (missing files and test setup).

**Step 3: Write minimal implementation**
Create Next.js app in `frontend/` directory using npm.
Write minimal `frontend/src/app/page.tsx`:
```tsx
export default function Page() {
  return (
    <main style={{ padding: '2rem' }}>
      <h1>OCR Invoice Processing</h1>
      <p>Upload an invoice to extract structured JSON data.</p>
    </main>
  );
}
```

**Step 4: Run test to verify it passes**
Run: `npm --prefix frontend test` (or validation check)
Expected: PASS

**Step 5: Commit**
```bash
git add frontend/
git commit -m "feat: initialize frontend nextjs project structure"
```

---

### Task 4: Define Invoice Data Models & Gemini Extraction Interface

**Files:**
- Create: `backend/src/main/java/com/example/ocr/model/InvoiceData.java`
- Create: `backend/src/main/java/com/example/ocr/service/GeminiOcrService.java`
- Create: `backend/src/main/java/com/example/ocr/service/GeminiOcrServiceImpl.java`
- Test: `backend/src/test/java/com/example/ocr/service/GeminiOcrServiceTest.java`

**Step 1: Write the failing test**
Create `backend/src/test/java/com/example/ocr/service/GeminiOcrServiceTest.java` to assert that the parsing of a mock image input yields a structured `InvoiceData` object matching SPEC-002:
```java
package com.example.ocr.service;

import com.example.ocr.model.InvoiceData;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockMultipartFile;
import static org.junit.jupiter.api.Assertions.*;

class GeminiOcrServiceTest {
    private final GeminiOcrService service = new GeminiOcrServiceImpl(null); // passing null for API key/client temporarily

    @Test
    void testMockExtraction() throws Exception {
        MockMultipartFile file = new MockMultipartFile("file", "invoice.png", "image/png", "mock content".getBytes());
        InvoiceData result = service.extractMock(file);
        assertNotNull(result);
        assertEquals("Mock Vendor", result.getVendor());
        assertEquals(550000.0, result.getTotal());
    }
}
```

**Step 2: Run test to verify it fails**
Run: `mvn -f backend/pom.xml test -Dtest=GeminiOcrServiceTest`
Expected: FAIL (missing classes and interface).

**Step 3: Write minimal implementation**
Create classes and interface.
`backend/src/main/java/com/example/ocr/model/InvoiceData.java`:
```java
package com.example.ocr.model;

import java.util.List;

public class InvoiceData {
    private String vendor;
    private String taxCode;
    private String invoiceNumber;
    private String date;
    private List<Item> items;
    private double subtotal;
    private double vat;
    private double total;

    // Getters, Setters

    public static class Item {
        private String name;
        private int quantity;
        private double unitPrice;
        private double total;
        // Getters, Setters
    }

    // getters and setters for InvoiceData
    public String getVendor() { return vendor; }
    public void setVendor(String vendor) { this.vendor = vendor; }
    public double getTotal() { return total; }
    public void setTotal(double total) { this.total = total; }
}
```

`backend/src/main/java/com/example/ocr/service/GeminiOcrService.java`:
```java
package com.example.ocr.service;

import com.example.ocr.model.InvoiceData;
import org.springframework.web.multipart.MultipartFile;
import java.io.IOException;

public interface GeminiOcrService {
    InvoiceData extract(MultipartFile file) throws IOException;
    InvoiceData extractMock(MultipartFile file) throws IOException;
}
```

`backend/src/main/java/com/example/ocr/service/GeminiOcrServiceImpl.java`:
```java
package com.example.ocr.service;

import com.example.ocr.model.InvoiceData;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import java.io.IOException;

@Service
public class GeminiOcrServiceImpl implements GeminiOcrService {
    public GeminiOcrServiceImpl(Object dummy) {}

    @Override
    public InvoiceData extract(MultipartFile file) throws IOException {
        return null;
    }

    @Override
    public InvoiceData extractMock(MultipartFile file) throws IOException {
        InvoiceData mock = new InvoiceData();
        mock.setVendor("Mock Vendor");
        mock.setTotal(550000.0);
        return mock;
    }
}
```

**Step 4: Run test to verify it passes**
Run: `mvn -f backend/pom.xml test -Dtest=GeminiOcrServiceTest`
Expected: PASS

**Step 5: Commit**
```bash
git add backend/src/main/java/com/example/ocr/model/InvoiceData.java backend/src/main/java/com/example/ocr/service/GeminiOcrService.java backend/src/main/java/com/example/ocr/service/GeminiOcrServiceImpl.java backend/src/test/java/com/example/ocr/service/GeminiOcrServiceTest.java
git commit -m "feat: define invoice data model and gemini service interface with mock extraction"
```

---

### Task 5: Implement Gemini API Real Client & Prompts

**Files:**
- Modify: `backend/src/main/java/com/example/ocr/service/GeminiOcrServiceImpl.java`
- Modify: `backend/src/main/resources/application.yml`
- Test: `backend/src/test/java/com/example/ocr/service/GeminiOcrServiceIntegrationTest.java`

**Step 1: Write failing integration test**
Create `backend/src/test/java/com/example/ocr/service/GeminiOcrServiceIntegrationTest.java` (using `@Disabled` by default or active key if available):
```java
package com.example.ocr.service;

import com.example.ocr.model.InvoiceData;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.mock.web.MockMultipartFile;
import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class GeminiOcrServiceIntegrationTest {
    @Autowired
    private GeminiOcrService service;

    @Test
    @Disabled("Needs actual GEMINI_API_KEY environment variable")
    void testRealExtraction() throws Exception {
        MockMultipartFile file = new MockMultipartFile("file", "test.png", "image/png", "dummy content".getBytes());
        InvoiceData result = service.extract(file);
        assertNotNull(result);
    }
}
```

**Step 2: Run test to verify it fails/disables correctly**
Run: `mvn -f backend/pom.xml test -Dtest=GeminiOcrServiceIntegrationTest`
Expected: PASS (since disabled, or FAIL if we force run without api key configured)

**Step 3: Implement client logic using WebClient/RestTemplate**
In `backend/src/main/java/com/example/ocr/service/GeminiOcrServiceImpl.java`, write code to encode the image to base64, construct the multi-modal payload for Gemini's API (`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent`), specify the JSON schema requirement, send the post request, and parse response into `InvoiceData`.

**Step 4: Run test to verify it passes**
Configure API key and run the integration test.
Expected: PASS

**Step 5: Commit**
```bash
git add backend/src/main/java/com/example/ocr/service/GeminiOcrServiceImpl.java backend/src/test/java/com/example/ocr/service/GeminiOcrServiceIntegrationTest.java
git commit -m "feat: implement gemini vision api client payload sending and response parsing"
```

---

### Task 6: Create REST Endpoint for Extraction

**Files:**
- Create: `backend/src/main/java/com/example/ocr/controller/OcrController.java`
- Test: `backend/src/test/java/com/example/ocr/controller/OcrControllerTest.java`

**Step 1: Write the failing test**
Create `backend/src/test/java/com/example/ocr/controller/OcrControllerTest.java`:
```java
package com.example.ocr.controller;

import com.example.ocr.service.GeminiOcrService;
import com.example.ocr.model.InvoiceData;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.multipart;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(OcrController.class)
class OcrControllerTest {
    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private GeminiOcrService service;

    @Test
    void testUploadAndExtract() throws Exception {
        MockMultipartFile file = new MockMultipartFile("file", "invoice.png", "image/png", "dummy".getBytes());
        InvoiceData data = new InvoiceData();
        data.setVendor("Test Vendor");

        Mockito.when(service.extract(Mockito.any())).thenReturn(data);

        mockMvc.perform(multipart("/api/extract").file(file))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.vendor").value("Test Vendor"));
    }
}
```

**Step 2: Run test to verify it fails**
Run: `mvn -f backend/pom.xml test -Dtest=OcrControllerTest`
Expected: FAIL (OcrController does not exist)

**Step 3: Write minimal implementation**
Create `backend/src/main/java/com/example/ocr/controller/OcrController.java`:
```java
package com.example.ocr.controller;

import com.example.ocr.model.InvoiceData;
import com.example.ocr.service.GeminiOcrService;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import java.io.IOException;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*")
public class OcrController {
    private final GeminiOcrService service;

    public OcrController(GeminiOcrService service) {
        this.service = service;
    }

    @PostMapping("/extract")
    public InvoiceData extract(@RequestParam("file") MultipartFile file) throws IOException {
        return service.extract(file);
    }
}
```

**Step 4: Run test to verify it passes**
Run: `mvn -f backend/pom.xml test -Dtest=OcrControllerTest`
Expected: PASS

**Step 5: Commit**
```bash
git add backend/src/main/java/com/example/ocr/controller/OcrController.java backend/src/test/java/com/example/ocr/controller/OcrControllerTest.java
git commit -m "feat: create /api/extract rest endpoint"
```

---

### Task 7: Next.js UI Drag-and-Drop Image Uploader & Extracted JSON Visualizer

**Files:**
- Modify: `frontend/src/app/page.tsx`
- Create: `frontend/src/app/components/Uploader.tsx`
- Create: `frontend/src/app/components/JsonViewer.tsx`

**Step 1: Write a smoke test for upload form**
Write simple rendering test in `frontend/src/app/components/Uploader.test.tsx` checking that dropzone is present.

**Step 2: Run test to verify it fails**
Run: `npm --prefix frontend test`
Expected: FAIL

**Step 3: Write UI Implementation**
- `Uploader`: Form allowing file selection or drag/drop of images. Sends file via `fetch` to `http://localhost:8080/api/extract`.
- `JsonViewer`: Renders result in a structured layout alongside the image preview. Shows structured fields (Vendor, Date, Items, Tax Code, Totals) in inputs allowing the user to inspect and edit.

**Step 4: Run tests and test locally**
Run the frontend locally: `npm run dev` in frontend, and `mvn spring-boot:run` in backend. Check integration.
Expected: PASS

**Step 5: Commit**
```bash
git add frontend/
git commit -m "feat: build Next.js upload and JSON visualization UI"
```
