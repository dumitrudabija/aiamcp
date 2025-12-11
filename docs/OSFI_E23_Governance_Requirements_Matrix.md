# OSFI E-23 Lifecycle Governance Requirements Matrix

**Reference:** OSFI Guideline E-23 – Model Risk Management (2027)
**Principle 2.3:** *"The scope, scale, and intensity of MRM should be commensurate with the risk introduced by the model"*

---

## Quick Reference Summary

| Stage | Requirement Area | Low | Medium | High | Critical |
|-------|-----------------|-----|--------|------|----------|
| **Design** | Approval Authority | Model owner | Model owner + risk | Senior risk committee | Executive/board |
| **Review** | Validation Independence | Self-review | Different team | Independent validation | External third-party |
| **Deployment** | Parallel Run Period | Not required | 2 weeks | 4 weeks | 8+ weeks |
| **Monitoring** | Performance Review | Annual | Quarterly | Monthly | Continuous + weekly |
| **Decommission** | Retention Period | 1 year | 3 years | 5 years | 7+ years |

---

## 1. DESIGN Stage Requirements

*OSFI Principles: 3.2 (Model Data), 3.3 (Model Development)*

| Requirement | Low Risk | Medium Risk | High Risk | Critical Risk |
|-------------|----------|-------------|-----------|---------------|
| **Documentation Depth** | Basic rationale | Detailed rationale + alternatives considered | Comprehensive design doc + risk analysis | Full design doc + board-level summary |
| **Data Quality Assessment** | Self-assessment sign-off | Documented review | Independent data review | Third-party data audit |
| **Bias/Fairness Analysis** | Not required | Initial screening | Comprehensive analysis | Pre-build fairness audit |
| **Approval Authority** | Model owner | Model owner + risk | Senior risk committee | Executive/board |

### Design Stage Checklist by Risk Level

#### Low Risk Models
- [ ] Document basic model rationale and business purpose
- [ ] Self-certify data quality meets standards
- [ ] Obtain model owner approval
- [ ] Assign model ID and register in inventory

#### Medium Risk Models
- [ ] Document detailed rationale with alternatives considered
- [ ] Perform documented data quality review
- [ ] Conduct initial bias/fairness screening
- [ ] Obtain model owner + risk function approval
- [ ] Document data lineage and provenance

#### High Risk Models
- [ ] Prepare comprehensive design document with risk analysis
- [ ] Commission independent data quality review
- [ ] Conduct comprehensive bias/fairness analysis
- [ ] Obtain senior risk committee approval
- [ ] Define monitoring criteria and thresholds
- [ ] Document all assumptions and limitations

#### Critical Risk Models
- [ ] Prepare full design document with board-level summary
- [ ] Commission third-party data audit
- [ ] Complete pre-build fairness audit
- [ ] Obtain executive/board approval
- [ ] Document explainability requirements
- [ ] Establish review standards for independent validation

---

## 2. REVIEW Stage Requirements

*OSFI Principle: 3.4 (Independent Validation)*

| Requirement | Low Risk | Medium Risk | High Risk | Critical Risk |
|-------------|----------|-------------|-----------|---------------|
| **Validation Independence** | Self-review acceptable | Different team | Independent validation function | External third-party |
| **Testing Scope** | Functional testing | Functional + performance | Full validation suite | Extended testing + stress scenarios |
| **Challenger Model** | Not required | Recommended | Required | Required + sensitivity analysis |
| **Explainability Review** | Output-level explanation | Documented | Demonstrated to stakeholders | Regulatory-ready |
| **Approval Authority** | Model owner | Validation + risk | Senior risk committee | Executive/board |

### Review Stage Checklist by Risk Level

#### Low Risk Models
- [ ] Complete self-review of model functionality
- [ ] Execute functional tests
- [ ] Document output-level explanations
- [ ] Obtain model owner sign-off

#### Medium Risk Models
- [ ] Assign reviewer from different team
- [ ] Execute functional and performance tests
- [ ] Develop challenger model (recommended)
- [ ] Document explainability methodology
- [ ] Obtain validation + risk sign-off

#### High Risk Models
- [ ] Engage independent validation function
- [ ] Execute full validation test suite
- [ ] Develop required challenger model
- [ ] Demonstrate explainability to stakeholders
- [ ] Obtain senior risk committee approval

#### Critical Risk Models
- [ ] Engage external third-party validator
- [ ] Execute extended testing with stress scenarios
- [ ] Complete challenger model + sensitivity analysis
- [ ] Prepare regulatory-ready explainability documentation
- [ ] Obtain executive/board approval

---

## 3. DEPLOYMENT Stage Requirements

*OSFI Principle: 3.5 (Quality and Change Control)*

| Requirement | Low Risk | Medium Risk | High Risk | Critical Risk |
|-------------|----------|-------------|-----------|---------------|
| **Environment Verification** | Configuration sign-off | Documented verification | Independent verification | Third-party audit |
| **Parallel Run Period** | Not required | 2 weeks | 4 weeks | 8+ weeks |
| **Rollback Capability** | Documented | Tested | Tested + drill | Tested + real-time capability |
| **Human Override Controls** | Optional | Available | Required + logged | Required + escalation path |
| **Go-Live Approval** | Model owner | Risk sign-off | Risk committee | Executive/board |

### Deployment Stage Checklist by Risk Level

#### Low Risk Models
- [ ] Sign off on production configuration
- [ ] Document rollback procedures
- [ ] Obtain model owner go-live approval
- [ ] Update model inventory with deployment date

#### Medium Risk Models
- [ ] Document environment verification
- [ ] Execute 2-week parallel run
- [ ] Test rollback procedures
- [ ] Implement human override capability
- [ ] Obtain risk function go-live sign-off

#### High Risk Models
- [ ] Obtain independent environment verification
- [ ] Execute 4-week parallel run
- [ ] Test rollback procedures + conduct drill
- [ ] Implement required human override with logging
- [ ] Obtain risk committee go-live approval

#### Critical Risk Models
- [ ] Commission third-party environment audit
- [ ] Execute 8+ week parallel run
- [ ] Verify real-time rollback capability
- [ ] Implement human override with escalation path
- [ ] Obtain executive/board go-live approval

---

## 4. MONITORING Stage Requirements

*OSFI Principle: 3.6 (Model Monitoring)*

| Requirement | Low Risk | Medium Risk | High Risk | Critical Risk |
|-------------|----------|-------------|-----------|---------------|
| **Performance Review Frequency** | Annual | Quarterly | Monthly | Continuous + weekly review |
| **Drift Monitoring** | Manual/periodic | Automated alerts | Real-time dashboards | Real-time + auto-throttle |
| **Fairness Monitoring** | Annual | Quarterly | Monthly | Continuous |
| **Incident Escalation Time** | 5 business days | 2 business days | 24 hours | Immediate |
| **Revalidation Trigger** | Major changes only | Material changes | Threshold breach | Any deviation |

### Monitoring Stage Checklist by Risk Level

#### Low Risk Models
- [ ] Schedule annual performance review
- [ ] Conduct manual/periodic drift checks
- [ ] Perform annual fairness review
- [ ] Escalate incidents within 5 business days
- [ ] Trigger revalidation for major changes only

#### Medium Risk Models
- [ ] Schedule quarterly performance reviews
- [ ] Configure automated drift alerts
- [ ] Conduct quarterly fairness monitoring
- [ ] Escalate incidents within 2 business days
- [ ] Trigger revalidation for material changes

#### High Risk Models
- [ ] Conduct monthly performance reviews
- [ ] Implement real-time drift dashboards
- [ ] Perform monthly fairness monitoring
- [ ] Escalate incidents within 24 hours
- [ ] Trigger revalidation on threshold breach

#### Critical Risk Models
- [ ] Implement continuous monitoring + weekly reviews
- [ ] Deploy real-time drift monitoring with auto-throttle
- [ ] Conduct continuous fairness monitoring
- [ ] Establish immediate incident escalation
- [ ] Trigger revalidation on any deviation

---

## 5. DECOMMISSION Stage Requirements

*OSFI Principle: 3.6 (Model Decommission)*

| Requirement | Low Risk | Medium Risk | High Risk | Critical Risk |
|-------------|----------|-------------|-----------|---------------|
| **Retention Period** | 1 year | 3 years | 5 years | 7+ years |
| **Documentation to Retain** | Model summary | Full documentation | Full + validation | Full + audit trail |
| **Stakeholder Notification** | Model users | + Risk function | + Senior management | + Regulators (if applicable) |
| **Downstream Impact Review** | Self-assessment | Documented review | Formal assessment | Independent review |

### Decommission Stage Checklist by Risk Level

#### Low Risk Models
- [ ] Archive model summary for 1 year
- [ ] Notify model users of retirement
- [ ] Complete self-assessment of downstream impacts
- [ ] Update model inventory status

#### Medium Risk Models
- [ ] Archive full documentation for 3 years
- [ ] Notify model users + risk function
- [ ] Document downstream impact review
- [ ] Confirm no residual dependencies

#### High Risk Models
- [ ] Archive full documentation + validation for 5 years
- [ ] Notify users + risk function + senior management
- [ ] Complete formal downstream impact assessment
- [ ] Obtain sign-off on decommission completion

#### Critical Risk Models
- [ ] Archive full documentation + audit trail for 7+ years
- [ ] Notify all stakeholders + regulators (if applicable)
- [ ] Commission independent downstream impact review
- [ ] Obtain executive sign-off on decommission

---

## Approval Authority Summary

| Stage | Low | Medium | High | Critical |
|-------|-----|--------|------|----------|
| Design | Model owner | Model owner + risk | Senior risk committee | Executive/board |
| Review | Model owner | Validation + risk | Senior risk committee | Executive/board |
| Deployment | Model owner | Risk sign-off | Risk committee | Executive/board |

---

## Important Notes

1. **Principle 2.3 Compliance**: Requirements scale with risk level. Higher risk models require more rigorous governance controls at each lifecycle stage.

2. **Risk Level Determination**: Use the 6 Risk Dimensions assessment framework (see `osfi_e23_risk_dimensions.py`) to determine model risk level.

3. **Customization Required**: These requirements are exemplification based on OSFI E-23 guidance. Financial institutions must customize thresholds, approval authorities, and specific requirements to align with their institutional risk framework.

4. **Professional Validation**: All assessments require validation by qualified model risk management professionals before regulatory compliance use.

---

*Document generated from OSFI E-23 MCP Server v3.x governance framework*
