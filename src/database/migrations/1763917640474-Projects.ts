import { MigrationInterface, QueryRunner } from "typeorm";

export class Projects1763917640474 implements MigrationInterface {
    name = 'Projects1763917640474'

    public async up(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`CREATE TYPE "public"."projects_status_enum" AS ENUM('ACTIVE', 'ONHOLD', 'COMPLETED')`);
        await queryRunner.query(`CREATE TABLE "projects" ("id" BIGSERIAL NOT NULL, "name" character varying(70) NOT NULL, "description" character varying NOT NULL, "start_date" TIMESTAMP NOT NULL, "end_date" TIMESTAMP NOT NULL, "status" "public"."projects_status_enum" NOT NULL, "created_at" TIMESTAMP NOT NULL DEFAULT now(), CONSTRAINT "PK_6271df0a7aed1d6c0691ce6ac50" PRIMARY KEY ("id"))`);
    }

    public async down(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`DROP TABLE "projects"`);
        await queryRunner.query(`DROP TYPE "public"."projects_status_enum"`);
    }

}
