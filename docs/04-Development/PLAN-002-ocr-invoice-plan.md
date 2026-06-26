# OCR Invoice Processing Monorepo Implementation Plan

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Build a monorepo containing a Spring Boot backend (Gradle Groovy, PostgreSQL) and a Next.js frontend (ESLint, Husky) that extracts structured JSON from invoice images using Gemini Vision API, with notifications routed to Hermes MCP and UI styling synchronized with Stitch MCP.

**Architecture:** A Next.js frontend allows users to upload invoice images, which are sent via REST to a Spring Boot backend. The backend forwards the image to the Gemini Vision API using a structured schema, validates calculations, stores the output in PostgreSQL, triggers a Hermes notification message, and returns the JSON to the client.

**Tech Stack:** Java 21, Spring Boot 3.3.1, Gradle (Groovy DSL), PostgreSQL, Next.js 14.2.x / 15.x (App Router), TypeScript, ESLint, Husky, Gemini API, Hermes MCP REST client, Stitch MCP.

---

### Task 1: Initialize Backend Project Structure (Gradle Groovy)

**Files:**
- Create: `apps/backend/build.gradle`
- Create: `apps/backend/settings.gradle`
- Create: `apps/backend/src/main/java/com/example/ocr/OcrApplication.java`
- Create: `apps/backend/src/main/resources/application.yml`
- Test: `apps/backend/src/test/java/com/example/ocr/OcrApplicationTests.java`

**Step 1: Write a minimal failing test**
Create `apps/backend/src/test/java/com/example/ocr/OcrApplicationTests.java`:
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
Run: `cd apps/backend && ./gradlew test` (or `gradlew.bat test` on Windows)
Expected: FAIL (No build file or gradle wrapper).

**Step 3: Write minimal implementation**
Create `apps/backend/build.gradle`:
```groovy
plugins {
    id 'java'
    id 'org.springframework.boot' version '3.3.1'
    id 'io.spring.dependency-management' version '1.1.5'
}

group = 'com.example'
version = '0.0.1-SNAPSHOT'
sourceCompatibility = '21'

repositories {
    mavenCentral()
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    runtimeOnly 'org.postgresql:postgresql'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
}

tasks.named('test') {
    useJUnitPlatform()
}
```
Create `apps/backend/settings.gradle`:
```groovy
rootProject.name = 'ocr-backend'
```
Create `apps/backend/src/main/java/com/example/ocr/OcrApplication.java`:
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
Create `apps/backend/src/main/resources/application.yml` with dynamic H2/PostgreSQL config.

**Step 4: Run test to verify it passes**
Run: `cd apps/backend && gradle test` (or setup gradlew)
Expected: PASS

**Step 5: Commit**
```bash
git add apps/backend/
git commit -m "feat: initialize backend spring boot project structure with gradle groovy"
```

---

### Task 2: Configure PostgreSQL Database & Entity

**Files:**
- Create: `apps/backend/src/main/java/com/example/ocr/model/Invoice.java`
- Create: `apps/backend/src/main/java/com/example/ocr/repository/InvoiceRepository.java`
- Modify: `apps/backend/src/main/resources/application.yml`
- Test: `apps/backend/src/test/java/com/example/ocr/repository/InvoiceRepositoryTest.java`

**Step 1: Write a failing repository test**
Create `apps/backend/src/test/java/com/example/ocr/repository/InvoiceRepositoryTest.java` testing invoice saving:
```java
package com.example.ocr.repository;

import com.example.ocr.model.Invoice;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import static org.junit.jupiter.api.Assertions.*;

@DataJpaTest
class InvoiceRepositoryTest {
    @Autowired
    private InvoiceRepository repository;

    @Test
    void testSaveInvoice() {
        Invoice invoice = new Invoice();
        invoice.setVendor("Test Vendor");
        invoice.setTotal(150000.0);
        Invoice saved = repository.save(invoice);
        assertNotNull(saved.getId());
    }
}
```

**Step 2: Run test to verify it fails**
Run: `cd apps/backend && gradle test --tests "com.example.ocr.repository.InvoiceRepositoryTest"`
Expected: FAIL (Compilation error - missing Entity/Repository classes).

**Step 3: Write minimal implementation**
Create Entity `apps/backend/src/main/java/com/example/ocr/model/Invoice.java` mapping the hybrid schema. Use Hibernate 6's JSON support for the `raw_payload` column:
```java
package com.example.ocr.model;

import jakarta.persistence.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;

@Entity
@Table(name = "invoices")
public class Invoice {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String vendor;
    private String taxCode;
    private String invoiceNumber;
    private LocalDate invoiceDate;
    private Double subtotal;
    private Double vat;
    private Double total;
    private String filePath;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "raw_payload", columnDefinition = "jsonb")
    private Map<String, Object> rawPayload;

    @OneToMany(mappedBy = "invoice", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<InvoiceItem> items;

    // Getters, setters, and constructors...
}
```
Create `apps/backend/src/main/java/com/example/ocr/model/InvoiceItem.java`:
```java
package com.example.ocr.model;

import jakarta.persistence.*;

@Entity
@Table(name = "invoice_items")
public class InvoiceItem {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "invoice_id")
    private Invoice invoice;

    private String name;
    private Double quantity;
    private Double unitPrice;
    private Double total;

    // Getters, setters, and constructors...
}
```
Create Repository `apps/backend/src/main/java/com/example/ocr/repository/InvoiceRepository.java`.
Configure local H2 database for tests and PostgreSQL parameters in `application.yml`.


**Step 4: Run test to verify it passes**
Run: `cd apps/backend && gradle test --tests "com.example.ocr.repository.InvoiceRepositoryTest"`
Expected: PASS

**Step 5: Commit**
```bash
git add apps/backend/src/main/java/com/example/ocr/model/Invoice.java apps/backend/src/main/java/com/example/ocr/repository/InvoiceRepository.java apps/backend/src/main/resources/application.yml
git commit -m "feat: configure postgresql entity and repository"
```

---

### Task 3: Initialize Next.js Frontend with ESLint & Husky

**Files:**
- Create: `apps/frontend/package.json`
- Create: `apps/frontend/.eslintrc.json`
- Create: `apps/frontend/.husky/pre-commit`
- Create: `apps/frontend/src/app/page.tsx`

**Step 1: Write a failing validation check**
Verify ESLint config exists and runs:
Run: `npm --prefix frontend run lint`
Expected: FAIL (missing eslint configuration or dependency packages).

**Step 2: Scaffold Next.js project with ESLint & Husky**
Run template setups.
Initialize husky in root or frontend.
Install eslint dependencies.

**Step 3: Run validation to verify it passes**
Run: `npm --prefix frontend run lint`
Expected: PASS (zero lint errors).

**Step 4: Commit**
```bash
git add apps/frontend/
git commit -m "feat: initialize nextjs frontend with eslint and husky pre-commit hooks"
```

---

### Task 4: Define Invoice Model & Mock Gemini Vision API Client

**Files:**
- Create: `apps/backend/src/main/java/com/example/ocr/model/InvoiceData.java`
- Create: `apps/backend/src/main/java/com/example/ocr/service/GeminiOcrService.java`
- Create: `apps/backend/src/main/java/com/example/ocr/service/GeminiOcrServiceImpl.java`
- Test: `apps/backend/src/test/java/com/example/ocr/service/GeminiOcrServiceTest.java`

**Step 1: Write failing service test**
Assert mock extraction yields structured model matching SPEC-002:
```java
package com.example.ocr.service;

import com.example.ocr.model.InvoiceData;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockMultipartFile;
import static org.junit.jupiter.api.Assertions.*;

class GeminiOcrServiceTest {
    private final GeminiOcrService service = new GeminiOcrServiceImpl();

    @Test
    void testMockExtraction() throws Exception {
        MockMultipartFile file = new MockMultipartFile("file", "invoice.png", "image/png", "dummy".getBytes());
        InvoiceData result = service.extractMock(file);
        assertNotNull(result);
        assertEquals("Mock Vendor", result.getVendor());
    }
}
```

**Step 2: Run test to verify it fails**
Run: `cd apps/backend && gradle test --tests "com.example.ocr.service.GeminiOcrServiceTest"`
Expected: FAIL

**Step 3: Write minimal implementation**
Implement classes matching parameters.

**Step 4: Run test to verify it passes**
Run: `cd apps/backend && gradle test --tests "com.example.ocr.service.GeminiOcrServiceTest"`
Expected: PASS

**Step 5: Commit**
```bash
git add apps/backend/
git commit -m "feat: define invoice data schemas and mock gemini service"
```

---

### Task 5: Implement Real Gemini API Client & Hermes MCP Integrator

**Files:**
- Modify: `apps/backend/src/main/java/com/example/ocr/service/GeminiOcrServiceImpl.java`
- Create: `apps/backend/src/main/java/com/example/ocr/service/HermesNotificationService.java`
- Test: `apps/backend/src/test/java/com/example/ocr/service/HermesNotificationServiceTest.java`

**Step 1: Write failing notification test**
Create `apps/backend/src/test/java/com/example/ocr/service/HermesNotificationServiceTest.java` verifying notification post requests:
```java
package com.example.ocr.service;

import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import static org.junit.jupiter.api.Assertions.*;

class HermesNotificationServiceTest {
    private final HermesNotificationService notificationService = Mockito.spy(new HermesNotificationService());

    @Test
    void testNotify() {
        notificationService.sendNotification("Extracted invoice successfully");
        Mockito.verify(notificationService, Mockito.times(1)).sendNotification(Mockito.anyString());
    }
}
```

**Step 2: Run test to verify it fails**
Expected: FAIL (missing class).

**Step 3: Implement real Gemini call & Hermes integration**
Add Gemini HTTP POST connection with JSON structured output parameters.
Write `HermesNotificationService` to send notification details via a configured REST client target or mock channel message payload.

**Step 4: Run test to verify it passes**
Run: `cd apps/backend && gradle test`
Expected: PASS

**Step 5: Commit**
```bash
git add apps/backend/
git commit -m "feat: integrate real gemini vision client and hermes notification connector"
```

---

### Task 6: Implement Endpoints and Next.js Front-End Integration

**Files:**
- Create: `apps/backend/src/main/java/com/example/ocr/controller/OcrController.java`
- Modify: `apps/frontend/src/app/page.tsx`
- Create: `apps/frontend/src/app/components/Uploader.tsx`

**Step 1: Write integration tests**
Verify frontend rendering and backend endpoint accessibility.

**Step 2: Run tests to verify they fail**
Expected: FAIL

**Step 3: Implement controller and UI**
Create `/api/extract` REST endpoint saving results into PostgreSQL and returning JSON output.
Create drag-and-drop Next.js UI using CSS, integrated with ESLint & Husky check constraints.

**Step 4: Run build & verify integration**
Verify system-wide integration, clean formatting, and run check lint rules.
Expected: PASS

**Step 5: Commit**
```bash
git add .
git commit -m "feat: complete end-to-end invoice extraction workflow with UI visualizer"
```
