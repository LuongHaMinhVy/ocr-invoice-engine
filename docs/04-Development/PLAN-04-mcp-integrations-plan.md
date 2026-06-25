# Email Intake & PostgreSQL MCP Integrations Implementation Plan

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Implement automated invoice intake by polling email attachments via Spring Integration IMAP and set up PostgreSQL MCP server for database validation.

**Architecture:** Add Spring Mail/Integration dependencies, implement an EmailIntakeService that polls unread emails for image/PDF attachments, saves them to temporary storage, and routes them to the OCR engine. Configure Postgres MCP server in settings.

**Tech Stack:** Spring Boot, Spring Integration Mail, JavaMail, PostgreSQL MCP.

---

### Task 1: Add Spring Integration Mail Dependencies

**Files:**
- Modify: `backend/build.gradle` (or the root `build.gradle` depending on setup)

**Step 1: Write the failing test / check dependency presence**
Verify that the `spring-boot-starter-integration` and `spring-integration-mail` are not yet in the project.
Run:
```powershell
Select-String -Path backend/build.gradle -Pattern "spring-integration-mail"
```
Expected: Pattern not found / blank output.

**Step 2: Add dependencies to build.gradle**
Add the following to the dependencies section:
```groovy
implementation 'org.springframework.boot:spring-boot-starter-integration'
implementation 'org.springframework.integration:spring-integration-mail'
```

**Step 3: Run build to verify dependencies compile successfully**
Run:
```powershell
./gradlew build -x test
```
Expected: BUILD SUCCESSFUL

**Step 4: Commit**
```bash
git add backend/build.gradle
git commit -m "feat: add Spring Integration Mail dependencies"
```

---

### Task 2: Implement Mail Configuration and Mail Receiver Config

**Files:**
- Create: `backend/src/main/resources/application-mail.yml`
- Create: `backend/src/main/java/com/example/ocr/config/MailReceiverConfig.java`

**Step 1: Write the failing test**
Create a config test file `backend/src/test/java/com/example/ocr/config/MailReceiverConfigTest.java` that asserts the MailReceiver bean is initialized.
Run:
```powershell
./gradlew test --tests com.example.ocr.config.MailReceiverConfigTest
```
Expected: FAIL due to missing config classes.

**Step 2: Implement MailReceiverConfig**
Create `MailReceiverConfig.java` and expose the IMAP integration flow:
```java
package com.example.ocr.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.integration.dsl.IntegrationFlow;
import org.springframework.integration.mail.dsl.Mail;

@Configuration
public class MailReceiverConfig {
    @Bean
    public IntegrationFlow imapMailFlow() {
        // Basic configuration skeleton for IMAP polling
        return IntegrationFlow.from(
            Mail.imapInboundAdapter("imaps://imap.gmail.com:993/INBOX")
                .searchTermStrategy((supportedFlags, folder) -> {
                    try {
                        return new javax.mail.search.FlagTerm(new javax.mail.Flags(javax.mail.Flags.Flag.SEEN), false);
                    } catch (Exception e) {
                        throw new IllegalStateException(e);
                    }
                }),
            e -> e.poller(p -> p.fixedDelay(300000)) // Poll every 5 minutes
        ).handle(message -> {
            // Processing handler placeholder
        }).get();
    }
}
```

**Step 3: Run test to verify passes**
Run:
```powershell
./gradlew test --tests com.example.ocr.config.MailReceiverConfigTest
```
Expected: PASS

**Step 4: Commit**
```bash
git add backend/src/main/resources/application-mail.yml backend/src/main/java/com/example/ocr/config/MailReceiverConfig.java backend/src/test/java/com/example/ocr/config/MailReceiverConfigTest.java
git commit -m "feat: configure IMAP mail flow configuration adapter"
```

---

### Task 3: Implement EmailIntakeService and Attachment Extraction

**Files:**
- Create: `backend/src/main/java/com/example/ocr/service/EmailIntakeService.java`
- Create: `backend/src/test/java/com/example/ocr/service/EmailIntakeServiceTest.java`

**Step 1: Write failing test**
Create a test that mocks `javax.mail.Message` containing a multipart body with a PDF attachment, and verifies that `EmailIntakeService.extractAttachments()` extracts it successfully.
Run:
```powershell
./gradlew test --tests com.example.ocr.service.EmailIntakeServiceTest
```
Expected: FAIL

**Step 2: Implement EmailIntakeService**
Implement parsing logic to extract attachments from MultiPart emails and save them to a temporary path, then forward the temp file to the OCR processing queue.
```java
package com.example.ocr.service;

import org.springframework.stereotype.Service;
import javax.mail.Message;
import javax.mail.MessagingException;
import javax.mail.Multipart;
import javax.mail.Part;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.List;

@Service
public class EmailIntakeService {
    public List<File> extractAttachments(Message message) throws MessagingException, IOException {
        List<File> files = new ArrayList<>();
        if (message.isMimeType("multipart/*")) {
            Multipart multipart = (Multipart) message.getContent();
            for (int i = 0; i < multipart.getCount(); i++) {
                Part part = multipart.getBodyPart(i);
                if (Part.ATTACHMENT.equalsIgnoreCase(part.getDisposition())) {
                    String fileName = part.getFileName();
                    if (fileName.endsWith(".pdf") || fileName.endsWith(".png") || fileName.endsWith(".jpg")) {
                        File tempFile = Files.createTempFile("email_ocr_", fileName).toFile();
                        part.writeTo(Files.newOutputStream(tempFile.toPath()));
                        files.add(tempFile);
                    }
                }
            }
        }
        return files;
    }
}
```

**Step 3: Run test**
Run:
```powershell
./gradlew test --tests com.example.ocr.service.EmailIntakeServiceTest
```
Expected: PASS

**Step 4: Commit**
```bash
git add backend/src/main/java/com/example/ocr/service/EmailIntakeService.java backend/src/test/java/com/example/ocr/service/EmailIntakeServiceTest.java
git commit -m "feat: implement email intake attachment extraction service"
```

---

### Task 4: Setup PostgreSQL MCP Configuration Guide

**Files:**
- Create: `docs/06-Maintenance/postgres-mcp-setup.md`

**Step 1: Write setup guide**
Create `docs/06-Maintenance/postgres-mcp-setup.md` with:
- Installation command: `npm install -g @modelcontextprotocol/server-postgres`
- Environment variables mapping configuration for cursor config settings.
- Verification queries to check table health.

**Step 2: Commit**
```bash
git add docs/06-Maintenance/postgres-mcp-setup.md
git commit -m "docs: add postgres-mcp-setup guide"
```
